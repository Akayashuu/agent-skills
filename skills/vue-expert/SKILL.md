---
name: vue-expert
description: Use when writing or reviewing Vue 3 components or composables — reaching for ref/reactive, computed, or watch; typing props/emits with script setup; wiring v-model or Pinia; or debugging lost reactivity, stale derived state, or destructured reactive objects.
---

# Vue Expert

## Overview

Idiomatic Vue 3 is **Composition API + `<script setup>` + TypeScript**, where reactivity is explicit and data flows one way. Most bugs come from breaking the reactivity proxy (destructuring a `reactive`/store, reassigning) or mirroring state with a watcher that should be a `computed`. Targets Vue 3.5+, where prop destructure is reactive and `useTemplateRef`/`onWatcherCleanup` exist. These are the judgment calls a linter can't make for you.

See `useExample.ts` for an idiomatic composable (typed, accepts `MaybeRefOrGetter`, self-cleaning).

## Quick Reference

| Goal | Do | Avoid |
|------|----|----|
| Local reactive state | `ref(x)` (works for any type) | `reactive({})` as the default |
| Derived value | `computed(() => …)` | `watch` that writes another ref |
| Typed props | `defineProps<Props>()` | runtime `props: {}` in TS, mutating a prop |
| Two-way binding | `defineModel<T>()` (3.4+) | manual `modelValue` + `update:` emit |
| Big/external object | `shallowRef` | deep `ref` on a 10k-row array |
| Destructure props with defaults (3.5+) | `const { x = 1 } = defineProps<P>()` | `withDefaults` boilerplate |
| Keep reactivity when destructuring | `toRefs` / `toRef`, `storeToRefs` | `const { x } = reactive(obj)` |
| Reuse logic | composable `useX()` returning refs | mixins |
| Shared app state | Pinia store | `provide`/`inject` sprawl |
| List rendering | `v-for` with stable `:key` | index keys, `v-if`+`v-for` same node |

## Core Patterns

**`ref` over `reactive` — reactive breaks on destructure/reassign:**
```ts
// ❌ destructuring or reassigning loses reactivity
const state = reactive({ count: 0 })
let { count } = state        // count is now a plain number, frozen
state = reactive({ count: 1 }) // reassign — template still sees the old proxy
// ✅ ref survives both; .value is the cost, predictability is the payoff
const count = ref(0)
count.value++                // reactive everywhere, reassignable
```

**`computed`, not a `watch` that mirrors state:**
```ts
// ❌ watcher duplicates source of truth, runs a tick late, can desync
const items = ref<Item[]>([])
const total = ref(0)
watch(items, (v) => { total.value = v.reduce((n, i) => n + i.price, 0) })
// ✅ derived, cached, always consistent — no extra ref, no flush timing
const total = computed(() => items.value.reduce((n, i) => n + i.price, 0))
```

**Typed props + emits, one-way data flow:**
```ts
// 3.5+: destructure stays reactive — compiler rewrites `count` to `props.count`.
// Native default syntax replaces withDefaults; reorder/omit props freely.
const { label, count = 0 } = defineProps<{ label: string; count?: number }>()
const emit = defineEmits<{ change: [value: number] }>()
// ❌ count++  — mutating a prop; parent owns it.
// ❌ watch(count, …) / passing `count` into a fn loses reactivity — wrap: watch(() => count, …)
function inc() { emit('change', count + 1) } // ✅ ask parent to change it
```

**`v-model` with `defineModel`:**
```ts
// ✅ replaces modelValue prop + update:modelValue emit boilerplate
const model = defineModel<string>({ required: true })
// parent: <SearchBox v-model="query" />; here just read/write model.value
```

**`watch` for side effects only, with cleanup:**
```ts
watch(id, async (newId) => {
  const ctrl = new AbortController()
  onWatcherCleanup(() => ctrl.abort()) // 3.5+: cancel stale request on re-run/unmount.
  // Must register BEFORE the first await — onWatcherCleanup only works synchronously.
  data.value = await fetchUser(newId, ctrl.signal)
})
```

## Common Mistakes

- **Forgetting `.value`** in `<script>` (templates auto-unwrap, JS does not) — `if (count > 0)` on a ref is always truthy.
- **Destructuring `reactive`** (or a Pinia store) — use `toRefs(state)` / `storeToRefs(store)`. Destructuring `defineProps` *is* reactive in 3.5+, but passing those vars into a function/`watch` still needs a `() =>` getter.
- **Template ref via raw `ref(null)` + matching name** — prefer `useTemplateRef('elName')` (3.5+) for clearer, decoupled element refs.
- **`watch` as a `computed`** — if the handler only sets another ref, it's derived state; use `computed`.
- **Index as `:key`** — reorders/insertions reuse the wrong DOM and component state. Use a stable id.
- **`v-if` + `v-for` on one element** — precedence is ambiguous; filter in a `computed` instead.
- **Deep `ref` on large/frozen data** — `shallowRef` avoids proxying every nested node.
- **Leaking watchers** created outside `setup` — keep the stop handle and call it, or scope with `effectScope`.

## When NOT to over-engineer

Don't reach for Pinia for state one component owns — a `ref` is enough. Don't wrap two lines in a composable; extract `useX` when logic is reused or genuinely complex. `watchEffect` is fine for fire-and-forget effects with auto-tracked deps; use explicit `watch` only when you need the old value or precise control. Reactivity is a tool, not a goal — the least reactive thing that stays correct wins.

## Sources

- [Reactivity Fundamentals](https://vuejs.org/guide/essentials/reactivity-fundamentals.html) — `ref` vs `reactive`, limitations of `reactive`
- [Props — Reactive Props Destructure (3.5)](https://vuejs.org/guide/components/props.html#reactive-props-destructure)
- [`<script setup>` — `defineModel` / `defineProps`](https://vuejs.org/api/sfc-script-setup.html)
- [Reactivity API: Core — `onWatcherCleanup`, `useTemplateRef`, `toValue`](https://vuejs.org/api/reactivity-core.html)
- [Watchers — side effects & cleanup](https://vuejs.org/guide/essentials/watchers.html)
- [Pinia — Setup Stores & `storeToRefs`](https://pinia.vuejs.org/core-concepts/)
