#!/usr/bin/env node
// Validates every skills/*/SKILL.md frontmatter and every .json file in the repo.
// Exits non-zero on any violation. No third-party deps (hand-rolled minimal YAML).

import { readdirSync, readFileSync, statSync } from 'node:fs';
import { join, dirname, basename, relative } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const errors = [];
let checks = 0;

function parseFrontmatter(src, file) {
  const m = src.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!m) {
    errors.push(`${file}: missing YAML frontmatter (--- block)`);
    return null;
  }
  const out = {};
  // Flat key: value frontmatter only (sufficient for SKILL.md).
  for (const raw of m[1].split(/\r?\n/)) {
    if (!raw.trim() || raw.trimStart().startsWith('#')) continue;
    const kv = raw.match(/^([A-Za-z0-9_-]+):\s?(.*)$/);
    if (!kv) {
      errors.push(`${file}: cannot parse frontmatter line: ${JSON.stringify(raw)}`);
      continue;
    }
    let val = kv[2].trim();
    if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
      val = val.slice(1, -1);
    }
    out[kv[1]] = val;
  }
  return out;
}

// --- SKILL.md validation ---
const skillsDir = join(root, 'skills');
const skillDirs = readdirSync(skillsDir).filter((d) => statSync(join(skillsDir, d)).isDirectory());
if (skillDirs.length === 0) errors.push('skills/ contains no skill directories');

for (const dir of skillDirs) {
  const file = join(skillsDir, dir, 'SKILL.md');
  let src;
  try {
    src = readFileSync(file, 'utf8');
  } catch {
    errors.push(`${dir}/SKILL.md: file not found`);
    continue;
  }
  checks++;
  const fm = parseFrontmatter(src, `${dir}/SKILL.md`);
  if (!fm) continue;
  if (!fm.name) errors.push(`${dir}/SKILL.md: frontmatter missing 'name'`);
  else if (fm.name !== dir) errors.push(`${dir}/SKILL.md: name '${fm.name}' != directory '${dir}'`);
  if (!fm.description) errors.push(`${dir}/SKILL.md: frontmatter missing 'description'`);
  else if (!fm.description.startsWith('Use when')) {
    errors.push(`${dir}/SKILL.md: description must start with "Use when" (got: ${JSON.stringify(fm.description.slice(0, 30))}...)`);
  }
}

// --- JSON validation (every .json in repo, excluding node_modules) ---
function walk(dir) {
  for (const entry of readdirSync(dir)) {
    if (entry === 'node_modules' || entry === '.git') continue;
    const p = join(dir, entry);
    const st = statSync(p);
    if (st.isDirectory()) walk(p);
    else if (entry.endsWith('.json')) {
      checks++;
      let txt = readFileSync(p, 'utf8');
      // tsconfig files are JSONC; strip comments before parsing.
      if (basename(p).includes('tsconfig')) {
        txt = txt.replace(/\/\*[\s\S]*?\*\//g, '').replace(/(^|[^:])\/\/.*$/gm, '$1');
      }
      try {
        JSON.parse(txt);
      } catch (e) {
        errors.push(`${relative(root, p)}: invalid JSON — ${e.message}`);
      }
    }
  }
}
walk(root);

if (errors.length) {
  console.error(`\nvalidate-skills: ${errors.length} violation(s):`);
  for (const e of errors) console.error(`  FAIL ${e}`);
  process.exit(1);
}
console.log(`validate-skills: PASS (${skillDirs.length} skills, ${checks} files checked)`);
