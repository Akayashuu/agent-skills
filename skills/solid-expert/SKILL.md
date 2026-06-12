---
name: solid-expert
description: Use when writing, reviewing, or debugging SolidJS — using createSignal/createMemo/createEffect, fine-grained reactivity, stores, props, or when reactivity silently stops updating.
---

# SolidJS Expert

## Overview

The #1 trap is treating Solid like React. **Components run ONCE.** There is no re-render, no virtual DOM, no dependency arrays. Reactivity is fine-grained: reading a signal *inside a tracking scope* (JSX, `createMemo`, `createEffect`) subscribes that exact spot, and only that spot updates. Most "Solid isn't updating" bugs come from breaking the subscription — destructuring props or reading a signal in code that runs once.

## Quick Reference

| Goal | Do | Avoid |
|------|----|----|
| Read a signal | call it: `count()` | `count` (that's the getter, not the value) |
| Use props | `props.x` lazily, or `splitProps`/`mergeProps` | destructuring `{ x }` (kills reactivity) |
| Derived/expensive value | `createMemo(() => …)` | recompute inline every read |
| Side effect | `createEffect` (runs after render, tracks deps) | doing effects in component body |
| Render a list | `<For each={items()}>` | `items().map(...)` |
| Conditional | `<Show when={ok()}>` | `{ok() && …}` ternary in once-run code |
| Nested reactive state | `createStore` + path setters | a signal holding a big object |
| Explicit dependencies | `on(dep, handler)` | relying on implicit tracking |
| Opt out of tracking | `untrack(() => …)` | reading then ignoring |

## Core Patterns

**Don't destructure props — it snapshots the value once and breaks reactivity:**
```tsx
// ❌ name is read once at call time; later updates never reach the DOM
function Hello({ name }: { name: string }) {
  return <h1>Hello {name}</h1>
}
// ✅ access lazily, or splitProps to keep reactive proxies intact
function Hello(props: { name: string; class?: string }) {
  const [local, rest] = splitProps(props, ['name'])
  return <h1 {...rest}>Hello {local.name}</h1> // re-reads on change
}
```

**Signals are getters — call them, and call them inside a tracking scope:**
```tsx
// ❌ destructured + read once in body; the <p> never updates
function Counter() {
  const [count] = createSignal(0)
  const doubled = count() * 2          // runs once, frozen
  return <p>{doubled}</p>
}
// ✅ read inside JSX (a tracking scope) or a memo
function Counter() {
  const [count, setCount] = createSignal(0)
  const doubled = createMemo(() => count() * 2)
  return <p onClick={() => setCount(count() + 1)}>{doubled()}</p>
}
```

**`<For>` over `.map()` — keyed by reference, rows persist instead of re-creating:**
```tsx
// ❌ .map() is evaluated once; the list never re-renders on change
<ul>{users().map(u => <li>{u.name}</li>)}</ul>
// ✅ <For> diffs by reference (use <Index> when keyed by position instead)
<For each={users()}>{(u) => <li>{u.name}</li>}</For>
```
`<For>` is keyed by item identity (reorders move DOM nodes); `<Index>` is keyed by position (the *item* is a signal `() => T`) — use it for primitives or fixed-length lists.

**`createStore` for nested objects — fine-grained, only touched paths update:**
```tsx
const [state, setState] = createStore({ user: { name: 'Ada', tags: ['a'] } })
setState('user', 'name', 'Grace')              // path setter, surgical
setState('user', 'tags', produce(t => t.push('b'))) // mutate-style via produce
```

## Common Mistakes

- **Destructuring props** — the canonical Solid bug. Keep `props` whole; use `mergeProps` for defaults, `splitProps` to forward.
- **Reading a signal without calling it** — `{count}` renders the function, never updates. It's `{count()}`.
- **`.map()`/ternary instead of `<For>`/`<Show>`** — runs once, won't react. Control-flow components subscribe.
- **Expecting the component body to re-run** — it runs once. Put reactive reads in JSX, `createMemo`, or `createEffect`.
- **Effects to compute values** — use `createMemo`. Reserve `createEffect` for genuine side effects (DOM, logging, fetch).
- **`createEffect` writing a signal it reads** — infinite loops; reach for `on()` with `defer`, or `untrack`. Batch grouped writes with `batch`.

## When NOT to over-engineer

`createMemo` has bookkeeping cost — don't wrap cheap expressions (`a() + b()`); only memo expensive work or values feeding many subscribers. A plain `() => …` derived accessor is often enough. Use `createStore` for genuinely nested state; a single signal is fine for flat values. Reach for `on()`/`untrack`/`batch` only when implicit tracking actually misbehaves, not preemptively.
