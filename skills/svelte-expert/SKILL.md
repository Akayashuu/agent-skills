---
name: svelte-expert
description: Use when writing, reviewing, or refactoring Svelte 5 components with runes — reaching for $state, $derived, $effect, $props, $bindable, snippets, stores, or shared reactive state in SvelteKit, or migrating legacy $:/export let code.
---

# Svelte Expert

## Overview

Svelte 5 replaces compiler-magic reactivity with explicit **runes**. The mental model is closer to fine-grained signals than to Svelte 4. Most "outdated" code uses `$:`, `export let`, and writable stores for local state — all now legacy. Reach for `$effect` rarely: it is for side effects, not for computing values (same smell as misused React effects).

## Quick Reference

| Goal | Do | Avoid |
|------|----|----|
| Reactive local state | `let x = $state(0)` | top-level `let` (no longer reactive) |
| Computed value | `$derived(a + b)` / `$derived.by(() => …)` | `$:` reactive statements |
| Component inputs | `let { x } = $props()` + TS type | `export let x` |
| Two-way binding | `let { v = $bindable() } = $props()` | manual event dispatch round-trips |
| Side effect / sync external | `$effect(() => …)` | using it to derive state |
| Effect cleanup | `return () => teardown()` | leaking listeners/timers |
| Shared reactive state | rune state in `.svelte.ts` module | writable store for everything |
| Cross-cutting / RxJS interop | `writable`/`readable` store | reinventing with runes |
| List rendering | `{#each items as it (it.id)}` | unkeyed `{#each}` |
| Reusable markup | `{#snippet}` / `{@render}` | slots (legacy) |

## Core Patterns

**State + derived — never compute with `$effect`:**
```svelte
<script lang="ts">
  // ❌ legacy + effect-as-derivation: extra render, stale risk
  // export let items: Item[];
  // $: total = items.reduce((n, i) => n + i.price, 0);
  // let count = 0;
  // $effect(() => { count = items.length; }); // wrong: derive, don't sync

  // ✅ runes
  let { items }: { items: Item[] } = $props();
  const total = $derived(items.reduce((n, i) => n + i.price, 0));
  const count = $derived(items.length);
</script>
```
> Runnable (state factory + `$derived` / `$derived.by`): [`examples/state-derived.svelte.ts`](./examples/state-derived.svelte.ts)

**`$props` with types and `$bindable` — replaces `export let`:**
```svelte
<script lang="ts">
  let {
    value = $bindable(''),     // two-way: <Input bind:value/>
    placeholder = 'Search',    // plain prop with default
    onsubmit,                  // callback prop, not createEventDispatcher
  }: { value?: string; placeholder?: string; onsubmit?: (v: string) => void } = $props();
</script>
```

**`$effect` only for external systems, with cleanup:**
```svelte
<script lang="ts">
  let { roomId }: { roomId: string } = $props();
  let messages = $state<Msg[]>([]);

  $effect(() => {
    const sock = connect(roomId);          // re-runs when roomId changes
    sock.on('msg', (m) => messages.push(m)); // deep proxy: mutate, don't reassign
    return () => sock.close();             // cleanup before re-run / unmount
  });
</script>
```
Use `$effect.pre(() => …)` (same API, runs *before* DOM updates) for the rare case of reading
layout before a render — e.g. capturing scroll position for autoscroll.
> Runnable (`$effect` cleanup + `$effect.pre`): [`examples/effect-cleanup.svelte.ts`](./examples/effect-cleanup.svelte.ts)

**Shared state — `.svelte.ts` module, not a store:**
```ts
// counter.svelte.ts
let count = $state(0);              // private: can't export a reassigned $state directly
export const counter = {
  get value() { return count; },   // getter exposes the live reactive read
  inc() { count++; },
};
// any component: import { counter } — reactive across the app
```
The compiler wraps reactivity per file, so a directly exported primitive `$state` won't
stay reactive when reassigned elsewhere. Export an **object** (mutate its fields) or a
**getter/function** API. See [`shared.svelte.ts`](./shared.svelte.ts) for both patterns.

**Fine-grained reactivity:** `$state` returns a deep proxy. Mutate in place (`obj.field = x`, `arr.push(...)`) — reassigning the whole object is unnecessary and loses fine-grained tracking. Use `(item.id)` keys in `{#each}` so Svelte moves DOM nodes instead of recreating and remounting them.

## Common Mistakes

- **`$:` / `export let` in new code** — Svelte 4 idioms; use `$derived` / `$props`.
- **`$effect` to derive state** — causes extra passes and stale values; use `$derived`/`$derived.by`.
- **Effect-driven loops** — an `$effect` that reads and writes the same `$state` loops infinitely. Prefer `$derived`; only if you *must* write state in an effect, read the looping dependency via `untrack(() => …)`. Runnable: [`examples/derived-not-effect.svelte.ts`](./examples/derived-not-effect.svelte.ts).
- **Writable store for component-local state** — use `$state`; reserve stores for cross-cutting concerns or external (RxJS) interop.
- **Reassigning whole objects** — breaks fine-grained updates; mutate proxy fields directly.
- **Unkeyed `{#each}`** — wrong DOM reuse on reorder; always provide `(item.id)`.
- **`createEventDispatcher` / slots** — replaced by callback props and snippets.

## When NOT to over-engineer

A small leaf component with one prop and no derived state needs no ceremony — `let { label } = $props()` is the whole story. Don't build a `.svelte.ts` store for state one component owns. Don't wrap `$derived` around a value used once inline. Runes are cheap; reach for shared modules and `$effect` only when something actually crosses component boundaries or touches the outside world.

## Sources

- [Runes — `$state`](https://svelte.dev/docs/svelte/$state) (incl. cross-module sharing gotcha)
- [`$derived` / `$derived.by`](https://svelte.dev/docs/svelte/$derived)
- [`$effect` / `$effect.pre`](https://svelte.dev/docs/svelte/$effect) ("when not to use", `untrack`)
- [`$props` / `$bindable`](https://svelte.dev/docs/svelte/$props)
- [Snippets — `{#snippet}` / `{@render}`](https://svelte.dev/docs/svelte/snippet) (slots deprecated)
