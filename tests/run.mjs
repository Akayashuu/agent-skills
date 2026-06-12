#!/usr/bin/env node
// Compile / type-check harness for reusable skill code artifacts.
// For each artifact: set up the correct tooling, type-check it, print PASS/FAIL/SKIP.
// Exits non-zero on any FAIL. Skips are explicit and printed with a reason.

import { execFileSync } from 'node:child_process';
import { mkdirSync, writeFileSync, readFileSync, rmSync, existsSync, cpSync, readdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const repo = join(here, '..');
const skills = join(repo, 'skills');
const work = join(here, '.work');
const tsc = join(here, 'node_modules', '.bin', 'tsc');

rmSync(work, { recursive: true, force: true });
mkdirSync(work, { recursive: true });

const results = [];
function record(name, status, detail) {
  results.push({ name, status, detail });
  const tag = status.padEnd(4);
  console.log(`${tag} ${name}${detail ? `  — ${detail}` : ''}`);
}

// Run tsc with an inline config; throws on type errors (output captured).
function runTsc(label, { files, compilerOptions, extraDir }) {
  const dir = join(work, label);
  mkdirSync(dir, { recursive: true });
  for (const f of files) {
    mkdirSync(dirname(join(dir, f.dest)), { recursive: true });
    cpSync(f.src, join(dir, f.dest));
  }
  if (extraDir) cpSync(extraDir, dir, { recursive: true });
  const cfg = {
    compilerOptions: { noEmit: true, skipLibCheck: true, ...compilerOptions },
    include: files.map((f) => f.dest),
  };
  writeFileSync(join(dir, 'tsconfig.json'), JSON.stringify(cfg, null, 2));
  try {
    execFileSync(tsc, ['-p', join(dir, 'tsconfig.json')], {
      cwd: here, // resolve node_modules from tests/
      stdio: 'pipe',
      encoding: 'utf8',
    });
    record(label, 'PASS');
    return true;
  } catch (e) {
    const out = `${e.stdout || ''}${e.stderr || ''}`.trim();
    record(label, 'FAIL', out.split('\n').slice(0, 12).join('\n      '));
    return false;
  }
}

const A = (sub) => join(skills, sub);

// Collect a skill's extracted examples (files under skills/<skill>/examples/) matching exts,
// as { src, dest } pairs with dest preserving the examples/ prefix. Empty if the dir is absent.
function examples(skill, exts) {
  const dir = A(`${skill}/examples`);
  if (!existsSync(dir)) return [];
  return readdirSync(dir)
    .filter((f) => exts.some((e) => f.endsWith(e)))
    .sort()
    .map((f) => ({ src: join(dir, f), dest: `examples/${f}` }));
}

// 1. typescript-expert — plain tsc, strict, using the skill's own tsconfig.base.json.
{
  const dir = join(work, 'typescript-expert');
  mkdirSync(join(dir, 'examples'), { recursive: true });
  cpSync(A('typescript-expert/types.ts'), join(dir, 'types.ts'));
  cpSync(A('typescript-expert/tsconfig.base.json'), join(dir, 'tsconfig.base.json'));
  // package.json "type":"module" so NodeNext resolves the examples' `../types.js` specifier to types.ts.
  writeFileSync(join(dir, 'package.json'), JSON.stringify({ type: 'module' }));
  const tsExamples = examples('typescript-expert', ['.ts']);
  for (const f of tsExamples) cpSync(f.src, join(dir, f.dest));
  writeFileSync(
    join(dir, 'tsconfig.json'),
    JSON.stringify({ extends: './tsconfig.base.json', compilerOptions: { noEmit: true, declaration: false, sourceMap: false }, include: ['types.ts', ...tsExamples.map((f) => f.dest)] }, null, 2),
  );
  try {
    execFileSync(tsc, ['-p', join(dir, 'tsconfig.json')], { cwd: here, stdio: 'pipe', encoding: 'utf8' });
    record('typescript-expert', 'PASS', 'via skill tsconfig.base.json (strict)');
  } catch (e) {
    const out = `${e.stdout || ''}${e.stderr || ''}`.trim();
    record('typescript-expert', 'FAIL', out.split('\n').slice(0, 12).join('\n      '));
  }
}

// 2. react-expert — @types/react, jsx: react-jsx.
runTsc('react-expert', {
  files: [{ src: A('react-expert/patterns.tsx'), dest: 'patterns.tsx' }, ...examples('react-expert', ['.ts', '.tsx'])],
  compilerOptions: {
    strict: true, target: 'ES2022', module: 'ESNext', moduleResolution: 'bundler',
    lib: ['ES2022', 'DOM', 'DOM.Iterable'], jsx: 'react-jsx',
  },
});

// 3. vue-expert — vue; ES2020 / ES2020+DOM / bundler.
runTsc('vue-expert', {
  files: [{ src: A('vue-expert/useExample.ts'), dest: 'useExample.ts' }, ...examples('vue-expert', ['.ts'])],
  compilerOptions: {
    strict: true, target: 'ES2020', module: 'ESNext', moduleResolution: 'bundler',
    lib: ['ES2020', 'DOM', 'DOM.Iterable'],
  },
});

// 4. solid-expert — solid-js; jsx preserve + jsxImportSource solid-js.
runTsc('solid-expert', {
  files: [{ src: A('solid-expert/primitives.ts'), dest: 'primitives.ts' }, ...examples('solid-expert', ['.ts', '.tsx'])],
  compilerOptions: {
    strict: true, target: 'ES2022', module: 'ESNext', moduleResolution: 'bundler',
    lib: ['ES2022', 'DOM', 'DOM.Iterable'], jsx: 'preserve', jsxImportSource: 'solid-js',
  },
});

// 5. angular-expert — standard (TC39) decorators, NO experimentalDecorators, strict.
runTsc('angular-expert', {
  files: [{ src: A('angular-expert/patterns.ts'), dest: 'patterns.ts' }, ...examples('angular-expert', ['.ts'])],
  compilerOptions: {
    strict: true, target: 'ES2022', module: 'ESNext', moduleResolution: 'bundler',
    lib: ['ES2022', 'DOM', 'DOM.Iterable'],
    experimentalDecorators: false, useDefineForClassFields: true,
  },
});

// 6. svelte-expert — .svelte.ts uses runes; plain tsc can't parse them.
//    Validate by compiling the module with svelte's compileModule API after stripping TS,
//    which is what actually proves the runes are well-formed.
{
  try {
    const { compileModule } = await import('svelte/compiler');
    const ts = await import('typescript');
    const mods = [
      { src: A('svelte-expert/shared.svelte.ts'), name: 'shared.svelte.js' },
      ...examples('svelte-expert', ['.svelte.ts']).map((f) => ({ src: f.src, name: f.dest.replace(/\.ts$/, '.js') })),
    ];
    for (const m of mods) {
      const srcTs = readFileSync(m.src, 'utf8');
      // Strip TS types -> JS, preserving rune calls, then let svelte validate the runes.
      const js = ts.default.transpileModule(srcTs, {
        compilerOptions: { target: ts.default.ScriptTarget.ESNext, module: ts.default.ModuleKind.ESNext },
      }).outputText;
      const { js: out } = compileModule(js, { filename: m.name, generate: 'client' });
      if (!out || !out.code) throw new Error(`svelte compileModule produced no output for ${m.name}`);
    }
    record('svelte-expert', 'PASS', `svelte compileModule (runes) — ${mods.length} module(s)`);
  } catch (e) {
    record('svelte-expert', 'FAIL', String(e.message || e).split('\n').slice(0, 8).join('\n      '));
  }
}

// 7. astro-expert — content.config.ts imports virtual modules (astro:content, astro/loaders).
//    `astro check` is the real validation but needs a full scaffolded project + is slow.
//    Reliable middle ground: tsc against Astro's shipped types via a triple-slash ref to
//    astro/client + an ambient shim for the virtual modules, proving the zod schema typechecks.
{
  const dir = join(work, 'astro-expert');
  mkdirSync(join(dir, 'examples'), { recursive: true });
  cpSync(A('astro-expert/content.config.ts'), join(dir, 'content.config.ts'));
  const astroExamples = examples('astro-expert', ['.ts']);
  for (const f of astroExamples) cpSync(f.src, join(dir, f.dest));
  // Ambient declarations for Astro's virtual modules (mirrors what `astro sync` generates).
  writeFileSync(
    join(dir, 'astro-virtual.d.ts'),
    [
      "// Ambient shims for Astro's virtual modules (mirrors `astro sync` output), typed",
      "// against the real `zod` so the schema callback's `image()` and z.* are checked.",
      "declare module 'astro:content' {",
      "  export const z: typeof import('zod').z;",
      "  interface SchemaContext { image: () => import('zod').ZodType<{ src: string; width: number; height: number; format: string }>; }",
      "  type Schema = import('zod').ZodType | ((ctx: SchemaContext) => import('zod').ZodType);",
      "  export function defineCollection<S extends Schema>(input: { loader?: unknown; type?: string; schema?: S }): { schema?: S };",
      "  export function reference(name: string): import('zod').ZodType;",
      "}",
      "declare module 'astro/loaders' {",
      "  export function glob(opts: { pattern: string | string[]; base?: string }): unknown;",
      "  export function file(path: string, opts?: unknown): unknown;",
      "}",
      '',
    ].join('\n'),
  );
  writeFileSync(
    join(dir, 'tsconfig.json'),
    JSON.stringify(
      {
        compilerOptions: {
          noEmit: true, skipLibCheck: true, strict: true,
          target: 'ES2022', module: 'ESNext', moduleResolution: 'bundler',
          lib: ['ES2022', 'DOM', 'DOM.Iterable'],
          types: [],
        },
        include: ['content.config.ts', 'astro-virtual.d.ts', ...astroExamples.map((f) => f.dest)],
      },
      null, 2,
    ),
  );
  const hasAstro = existsSync(join(here, 'node_modules', 'astro'));
  const hasZod = existsSync(join(here, 'node_modules', 'zod'));
  if (!hasAstro || !hasZod) {
    record('astro-expert', 'SKIP', `missing dep(s): ${[!hasAstro && 'astro', !hasZod && 'zod'].filter(Boolean).join(', ')}`);
  } else {
    try {
      execFileSync(tsc, ['-p', join(dir, 'tsconfig.json')], { cwd: here, stdio: 'pipe', encoding: 'utf8' });
      record('astro-expert', 'PASS', 'tsc vs astro/zod types + virtual-module shims (astro check is slower, not run in CI)');
    } catch (e) {
      const out = `${e.stdout || ''}${e.stderr || ''}`.trim();
      record('astro-expert', 'FAIL', out.split('\n').slice(0, 12).join('\n      '));
    }
  }
}

// 8. takt-expert — markdown, no compile. Verify referenced npm packages resolve.
{
  const md = readFileSync(A('takt-expert/snippets.md'), 'utf8');
  const pkgs = [...new Set([...md.matchAll(/@vskstudio\/takt-[a-z]+/g)].map((m) => m[0]))].sort();
  if (process.env.SKIP_NPM_CHECK === '1') {
    record('takt-expert', 'SKIP', `npm existence check skipped (SKIP_NPM_CHECK=1); packages referenced: ${pkgs.join(', ')}`);
  } else {
    const missing = [];
    for (const p of pkgs) {
      try {
        execFileSync('npm', ['view', p, 'version'], { stdio: 'pipe', encoding: 'utf8', timeout: 30000 });
      } catch {
        missing.push(p);
      }
    }
    if (missing.length) {
      record('takt-expert', 'FAIL', `not found on npm: ${missing.join(', ')}`);
    } else {
      record('takt-expert', 'PASS', `${pkgs.length} @vskstudio/takt-* packages exist on npm`);
    }
  }
}

// 8b. takt-expert examples — plain-TS core usage type-checked against @vskstudio/takt-core.
{
  const taktExamples = examples('takt-expert', ['.ts']);
  if (!taktExamples.length) {
    // nothing to do
  } else if (!existsSync(join(here, 'node_modules', '@vskstudio', 'takt-core'))) {
    record('takt-expert/examples', 'SKIP', 'missing dep: @vskstudio/takt-core');
  } else {
    runTsc('takt-expert/examples', {
      files: taktExamples,
      compilerOptions: {
        strict: true, target: 'ES2020', module: 'ESNext', moduleResolution: 'bundler',
        lib: ['ES2020', 'DOM', 'DOM.Iterable'],
      },
    });
  }
}

rmSync(work, { recursive: true, force: true });

const failed = results.filter((r) => r.status === 'FAIL');
const skipped = results.filter((r) => r.status === 'SKIP');
console.log(`\n${results.length} artifacts: ${results.filter((r) => r.status === 'PASS').length} PASS, ${failed.length} FAIL, ${skipped.length} SKIP`);
if (failed.length) {
  console.error(`harness: FAILED (${failed.map((r) => r.name).join(', ')})`);
  process.exit(1);
}
console.log('harness: OK');
