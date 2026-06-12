// shared.svelte.ts — rune-based shared state, the modern replacement for writable stores.
//
// WHY: In Svelte 5 you no longer need `writable()` for app-wide state. A `.svelte.ts`
// (or .svelte.js) module compiles runes just like a component, so `$state`/`$derived`
// here are reactive everywhere they're imported — no `.subscribe`, no `$store` autosub,
// no manual unsubscribe.
//
// GOTCHA: the compiler processes one file at a time, so it can't wrap reassignments of an
// exported primitive across module boundaries. You CANNOT do `export let count = $state(0)`
// and mutate it from another file. Two safe patterns:
//   1. export an OBJECT held in $state and mutate its fields (proxy stays reactive), or
//   2. keep the primitive module-private and expose a getter (function or `get` accessor).
// Both are shown below.

// ── Pattern 1: exported $state object (mutate fields directly) ───────────────
export const settings = $state({
  theme: 'light' as 'light' | 'dark',
  compact: false,
});
// Reassigning `settings.theme` from any component just works — it's a deep proxy.

// ── Pattern 2: private primitive + getter-based API (store-like surface) ─────
let count = $state(0);
const doubled = $derived(count * 2); // recomputes lazily when `count` changes

export const counter = {
  // getters expose live reactive reads without leaking the writable binding
  get value() {
    return count;
  },
  get doubled() {
    return doubled;
  },
  increment() {
    count += 1;
  },
  reset() {
    count = 0;
  },
};

// Usage in a component:
//   import { counter, settings } from './shared.svelte.ts';
//   <button onclick={counter.increment}>{counter.value} ({counter.doubled})</button>
//   <input type="checkbox" bind:checked={settings.compact} />
