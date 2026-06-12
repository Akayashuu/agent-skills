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

**Shared state — `.svelte.ts` module, not a store:**
```ts
// counter.svelte.ts
let count = $state(0);
export const counter = {
  get value() { return count; },
  inc() { count++; },
};
// any component: import { counter } — reactive across the app
```

**Fine-grained reactivity:** `$state` returns a deep proxy. Mutate in place (`obj.field = x`, `arr.push(...)`) — reassigning the whole object is unnecessary and loses fine-grained tracking. Use `(item.id)` keys in `{#each}` so Svelte moves DOM nodes instead of recreating and remounting them.

## Common Mistakes

- **`$:` / `export let` in new code** — Svelte 4 idioms; use `$derived` / `$props`.
- **`$effect` to derive state** — causes extra passes and stale values; use `$derived`/`$derived.by`.
- **Effect-driven loops** — an `$effect` that writes state it also reads. Read once with `untrack(() => …)` or restructure as `$derived`.
- **Writable store for component-local state** — use `$state`; reserve stores for cross-cutting concerns or external (RxJS) interop.
- **Reassigning whole objects** — breaks fine-grained updates; mutate proxy fields directly.
- **Unkeyed `{#each}`** — wrong DOM reuse on reorder; always provide `(item.id)`.
- **`createEventDispatcher` / slots** — replaced by callback props and snippets.

## When NOT to over-engineer

A small leaf component with one prop and no derived state needs no ceremony — `let { label } = $props()` is the whole story. Don't build a `.svelte.ts` store for state one component owns. Don't wrap `$derived` around a value used once inline. Runes are cheap; reach for shared modules and `$effect` only when something actually crosses component boundaries or touches the outside world.
