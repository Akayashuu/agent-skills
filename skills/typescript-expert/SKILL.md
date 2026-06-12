---
name: typescript-expert
description: Use when writing, reviewing, or refactoring TypeScript — choosing between types/interfaces, modelling data, designing generics/APIs, or fixing `any`, weak unions, enum, and unsound type assertions.
---

# TypeScript Expert

## Overview

Idiomatic TypeScript is about **making illegal states unrepresentable** and letting inference do the work. The compiler is a design tool, not a formality. These are the judgment calls a linter can't make for you.

## Quick Reference

| Goal | Do | Avoid |
|------|----|----|
| Closed set of values | union literals `'a' \| 'b'` or `as const` object | `enum` |
| Validate a literal against a type | `satisfies T` | `: T` (widens) or `as T` (lies) |
| Untrusted input | `unknown` + narrow | `any` |
| Variant data | discriminated union (`kind` tag) | optional flags / many `?:` |
| Distinct primitives (ids, tokens) | branded type | bare `string`/`number` |
| Object shape | `interface` (extensible, faster errors) | `type` for plain objects |
| Union/mapped/conditional | `type` | `interface` (can't express it) |
| Import only types | `import type {…}` | value import (emits a phantom runtime import) |
| Exhaustive switch | `default: assertNever(x)` | no default |
| Block inference from an arg | `NoInfer<T>` on the slave position | letting a default/fallback widen `T` |
| Infer literals at the signature | `<const T>` type param | forcing callers to write `as const` |
| Scoped cleanup (files, locks, spans) | `using` / `await using` | manual `try/finally` |

## Core Patterns

**Discriminated unions over flag soup** — illegal combinations stop compiling:
```ts
// ❌ allows { loading: true, data: [...] } — a contradiction
type State = { loading: boolean; error?: string; data?: User[] }
// ✅ each variant carries exactly its own data
type State =
  | { status: 'loading' }
  | { status: 'error'; message: string }
  | { status: 'success'; data: User[] }
```

**Exhaustiveness — new variants become compile errors, not silent bugs:**
```ts
switch (state.status) {
  case 'loading': return …
  case 'error':   return …
  case 'success': return …
  default: return assertNever(state) // add a variant → error here
}
```
`assertNever`, the `Brand<T,B>` helper, and `Result/ok/err` live in [`types.ts`](./types.ts) — copy it in.

**`satisfies` — check without widening, keep the literal type:**
```ts
const config = { port: 3000, host: 'localhost' } satisfies Record<string, string | number>
config.port // still `number`, not `string | number`
```

**`NoInfer<T>` — pin the generic from one argument, only check the other:**
```ts
function on<E extends string>(events: E[], initial: NoInfer<E>) { /* … */ }
on(['a', 'b'], 'c') // ❌ 'c' can't widen E; must be 'a' | 'b'
```

**`using` — deterministic cleanup, LIFO at scope end, even on throw/early-return:**
```ts
{
  using span = tracer.start('work') // span[Symbol.dispose]() runs automatically
  using lock = await mutex.acquire()
} // disposed lock-then-span here — no try/finally
```
Use `await using` for `Symbol.asyncDispose`. Needs `lib: ["ESNext.Disposable"]`.

**Generics: constrain and infer, don't over-parameterize.** A type parameter used once is usually wrong — it should appear in ≥2 positions (input→output) to relate them. Constrain with `extends` so the body can use the shape.

## Common Mistakes

- **`as` to silence errors** — an assertion is an unchecked claim. If you must, the only safe widening cast is to `unknown` first; otherwise narrow with a type guard (`x is T`).
- **`enum`** — emits runtime code, has nominal/structural surprises, doesn't tree-shake. Use `as const` objects or union literals.
- **`any` anywhere** — it disables checking transitively. Use `unknown` at boundaries and narrow.
- **Over-typing** — don't restate what inference already knows (`const n: number = 5`). Annotate function **parameters and public return types**; let locals infer.
- **`Function`, `object`, `{}`** — too loose. Use precise signatures / `Record<K,V>` / `unknown`.
- **Non-null `!` to chase undefined** — fix the type or narrow; `!` hides the real nullability.
- **`Promise` without `await`/return** — enable `no-floating-promises`; an unhandled rejection is silent.

## When NOT to over-engineer

Branded types, deep conditional types, and template-literal type gymnastics have a real readability cost. Reach for them when they prevent a class of real bugs — not to show the type system can do it. If a type is harder to read than the bug it prevents, simplify.

## tsconfig baseline

`strict: true` is the floor. Add `noUncheckedIndexedAccess` (`arr[i]` is `T | undefined`), `exactOptionalPropertyTypes` (`x?:` can't be explicitly set to `undefined`), and `verbatimModuleSyntax` (forces `import type`, no phantom runtime imports). These catch real bugs default strict misses. A ready-to-extend [`tsconfig.base.json`](./tsconfig.base.json) is in this dir.

> Versions: `satisfies` (4.9), const type params (5.0), `using`/`await using` (5.2), `NoInfer` (5.4). All stable on the current 5.x/6.x line.

## Sources

- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html) · [Utility Types](https://www.typescriptlang.org/docs/handbook/utility-types.html) (`NoInfer`)
- [tsconfig reference](https://www.typescriptlang.org/tsconfig/) — flag semantics
- [TS 4.9 release notes](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-9.html) — `satisfies`
- [TS 5.0 release notes](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-0.html) — const type parameters
- [TS 5.2 release notes](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-2.html) — `using` / explicit resource management
