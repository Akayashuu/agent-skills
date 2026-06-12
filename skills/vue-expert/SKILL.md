---
name: vue-expert
description: Use when writing or reviewing Vue 3 components or composables — reaching for ref/reactive, computed, or watch; typing props/emits with script setup; wiring v-model or Pinia; or debugging lost reactivity, stale derived state, or destructured reactive objects.
---

# Vue Expert

## Overview

Idiomatic Vue 3 is **Composition API + `<script setup>` + TypeScript**, where reactivity is explicit and data flows one way. Most bugs come from breaking the reactivity proxy (destructuring, reassigning) or mirroring state with a watcher that should be a `computed`. These are the judgment calls a linter can't make for you.

## Quick Reference

| Goal | Do | Avoid |
|------|----|----|
| Local reactive state | `ref(x)` (works for any type) | `reactive({})` as the default |
| Derived value | `computed(() => …)` | `watch` that writes another ref |
| Typed props | `defineProps<Props>()` | runtime `props: {}` in TS, mutating a prop |
| Two-way binding | `defineModel<T>()` (3.4+) | manual `modelValue` + `update:` emit |
| Big/external object | `shallowRef` | deep `ref` on a 10k-row array |
| Keep reactivity when destructuring | `toRefs` / `toRef` | `const { x } = reactive(obj)` |
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
const props = withDefaults(defineProps<{ label: string; count?: number }>(), { count: 0 })
const emit = defineEmits<{ change: [value: number] }>()
// ❌ props.count++  — mutating a prop; parent owns it
function inc() { emit('change', props.count + 1) } // ✅ ask parent to change it
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
  onWatcherCleanup(() => ctrl.abort()) // cancel stale request on re-run/unmount
  data.value = await fetchUser(newId, ctrl.signal)
})
```

## Common Mistakes

- **Forgetting `.value`** in `<script>` (templates auto-unwrap, JS does not) — `if (count > 0)` on a ref is always truthy.
- **Destructuring `reactive`** or props — use `toRefs(state)` / `toRef(props, 'x')` to keep the link.
- **`watch` as a `computed`** — if the handler only sets another ref, it's derived state; use `computed`.
- **Index as `:key`** — reorders/insertions reuse the wrong DOM and component state. Use a stable id.
- **`v-if` + `v-for` on one element** — precedence is ambiguous; filter in a `computed` instead.
- **Deep `ref` on large/frozen data** — `shallowRef` avoids proxying every nested node.
- **Leaking watchers** created outside `setup` — keep the stop handle and call it, or scope with `effectScope`.

## When NOT to over-engineer

Don't reach for Pinia for state one component owns — a `ref` is enough. Don't wrap two lines in a composable; extract `useX` when logic is reused or genuinely complex. `watchEffect` is fine for fire-and-forget effects with auto-tracked deps; use explicit `watch` only when you need the old value or precise control. Reactivity is a tool, not a goal — the least reactive thing that stays correct wins.
