---
name: react-expert
description: Use when writing, reviewing, or refactoring React components — taming re-renders, deciding what belongs in state vs derived during render, fixing useEffect overuse/race conditions, key/list bugs, useMemo/useCallback noise, context, refs, or server vs client component ("use client") boundaries.
---

# React Expert

## Overview

Idiomatic React is **derive, don't store; render, don't sequence.** Most state is redundant and most effects are a smell — the UI is a pure function of props, state, and context, and `useEffect` exists only to sync with systems *outside* React. These are the judgment calls a linter can't make for you.

## Quick Reference

| Goal | Do | Avoid |
|------|----|----|
| Value computable from props/state | compute in render | `useState` + `useEffect` to "keep it updated" |
| React to a prop/state change | derive in render, or `key` to reset | `useEffect` watching that value |
| Talk to a non-React system | `useEffect` (subscriptions, DOM, timers) | effects for data transforms |
| List items | stable id `key` | `key={index}` |
| Fetch data | framework / TanStack Query / RSC | hand-rolled `useEffect` + `fetch` |
| Avoid prop-drilling | composition (`children`) then context | one giant global context |
| Expensive recompute / referential dep | `useMemo`/`useCallback` with a real reason | memoizing everything by default |
| Form input | controlled, or uncontrolled + `ref` | mixing both on one field |
| Read latest props/state inside an Effect | `useEffectEvent` (stable in 19.2) | widening effect deps to silence the linter |

## Core Patterns

**Derive during render — don't mirror props/state into an effect.** The effect runs *after* paint, so the UI flashes a stale value, and the extra render is pure waste:
```tsx
// ❌ redundant state + effect: extra render, stale frame, easy to desync
function Cart({ items }: { items: Item[] }) {
  const [total, setTotal] = useState(0)
  useEffect(() => { setTotal(items.reduce((s, i) => s + i.price, 0)) }, [items])
  return <p>{total}</p>
}
// ✅ it's just a value; compute it. Wrap in useMemo only if profiling says so.
const total = items.reduce((s, i) => s + i.price, 0)
```
> Runnable: [`examples/derive-during-render.tsx`](./examples/derive-during-render.tsx)

**Reset state on identity change with `key`, not an effect.** Changing the `key` remounts the subtree, discarding old state — no manual resync:
```tsx
// ❌ effect to "reset form when user changes" — stale between switch and effect
useEffect(() => { setDraft('') }, [userId])
// ✅ a different user is a different form; let React remount it
<ProfileForm key={userId} />
```
> Runnable: [`examples/reset-with-key.tsx`](./examples/reset-with-key.tsx)

**Effects are for external systems — and must clean up to dodge races.** Anything async needs an ignore flag or `AbortController`, which is exactly why a data library is better:
```tsx
// ❌ no cleanup: a slow earlier request resolves last and overwrites the new one
useEffect(() => { fetch(`/api/u/${id}`).then(r => r.json()).then(setUser) }, [id])
// ✅ ignore stale resolutions (or just use TanStack Query / an RSC loader)
```
> Runnable: [`examples/abortable-effect-fetch.tsx`](./examples/abortable-effect-fetch.tsx)

**Composition kills prop-drilling before context does.** Pass rendered UI as `children` so intermediate components never see props they only forward:
```tsx
// ❌ Layout threads `user` through just to hand it down
<Layout user={user} />  // Layout forwards user → Sidebar → Avatar
// ✅ render the leaf where the data lives; Layout stays agnostic
<Layout sidebar={<Avatar user={user} />} />
```

**Separate non-reactive logic with `useEffectEvent` — don't lie to the deps array.** Stable since React 19.2: an Effect Event always sees the latest props/state but isn't reactive, so it stays *out* of the deps array — for fresh values an Effect shouldn't re-synchronize on:
```tsx
const onConnected = useEffectEvent(() => log('connected', theme)) // reads latest theme
useEffect(() => {
  const conn = createConnection(roomId)
  conn.on('connected', () => onConnected())
  conn.connect()
  return () => conn.disconnect()
}, [roomId]) // re-runs on roomId only; theme change does NOT reconnect
```
> Runnable: [`examples/use-effect-event.tsx`](./examples/use-effect-event.tsx)

**Memoize for referential stability, not "speed."** A `useCallback`/`useMemo` matters when its result is a dependency of a memoized child or another hook — otherwise it's noise that adds its own cost:
```tsx
const onSelect = useCallback((id: string) => dispatch(select(id)), [dispatch]) // stable prop for memo'd <Row>
```
**React Compiler (1.0, stable Oct 2025) changes this calculus.** It auto-memoizes at build time, so with the compiler on you can delete most hand-written `useMemo`/`useCallback`/`React.memo`. Keep them only where it bails out (components that break the Rules of React). The compiler optimizes; it won't fix stored derived state or over-broad effect deps.

## Common Mistakes

- **`useEffect` to compute derived data** — transform in render; effects are for syncing with the outside world.
- **`key={index}`** — on reorder/insert, React reuses the wrong DOM/state. Use a stable id.
- **Stale closures** — a callback captures the render's values; reading "latest" inside an Effect is what `useEffectEvent` is for — not a lie to the deps array.
- **Over-broad or missing deps** — don't silence `react-hooks/exhaustive-deps`; fix the design (move logic out, use a ref, or a functional `setState(prev => …)`).
- **`setState` during render** without a guard → infinite loop. Derive instead.
- **Premature `memo`/`useMemo` everywhere** — measure first; memoization isn't free.
- **One giant context** — every consumer re-renders on any field change. Split by concern (or by state vs dispatch).
- **`ref` for things render should own** — refs are an imperative escape hatch (focus, measure, integrate non-React libs), not a place to stash render data.
- **Reading data in a Server Component then marking the whole tree `'use client'`** — keep `'use client'` at the interactive leaf; fetch on the server.

## When NOT to over-engineer

Local, cheap, self-contained UI state (a toggle, an input) needs no reducer, no context, no memo. Reach for `useReducer`, context splitting, or a data library when state is shared, complex, or async — not preemptively. In React 19 (stable), prefer the platform: `use` to unwrap promises/context, `<form>` Actions + `useActionState` for submission and pending UI, `useOptimistic` for optimistic updates, ref-as-prop (no more `forwardRef`), and Server Components to fetch on the server so the client ships less and avoids effect-based fetching entirely. Don't hand-roll what the framework now does.

See `examples/` for self-contained, compiling versions of each pattern above (and `patterns.tsx` for the same three combined in one module).

## Sources

- [You Might Not Need an Effect](https://react.dev/learn/you-might-not-need-an-effect)
- [Synchronizing with Effects](https://react.dev/learn/synchronizing-with-effects)
- [Separating Events from Effects](https://react.dev/learn/separating-events-from-effects) · [`useEffectEvent`](https://react.dev/reference/react/useEffectEvent)
- [React v19 (stable)](https://react.dev/blog/2024/12/05/react-19) · [React 19.2](https://react.dev/blog/2025/10/01/react-19-2)
- [React Compiler v1.0](https://react.dev/blog/2025/10/07/react-compiler-1)
