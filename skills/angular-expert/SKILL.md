---
name: angular-expert
description: Use when writing, reviewing, or refactoring Angular — standalone components, signals, RxJS streams, change detection, or dependency injection with inject(), and new control flow (@if/@for/@switch).
---

# Angular Expert

## Overview

Modern Angular (v20+, current stable v22 as of mid-2026) is a different framework from the NgModule era. State lives in **signals**, components are **standalone** (standalone is the default and the `standalone` flag is no longer needed in v19+), DI uses the **`inject()`** function, and templates use **`@if`/`@for`/`@switch`**. New code that reaches for `NgModule`, `@Input()` decorators, or `*ngFor` is already legacy. These are the choices the CLI scaffolder won't always make for you.

**Stability landmarks** (per angular.dev): signals (`signal`/`computed`/`effect`/`linkedSignal`), signal inputs/outputs, and signal queries are **stable since v20**. `resource()` is **stable since v22**; `httpResource()` ships alongside it. **Zoneless** change detection (`provideZonelessChangeDetection()`) is **stable since v20.2 and the default in v21+** — no `zone.js`. `OnPush` is still recommended and expected to become the default.

## Quick Reference

| Goal | Do | Avoid |
|------|----|----|
| Component packaging | standalone (default v19+; flag implicit) | `NgModule` declarations |
| Local/derived state | `signal()`, `computed()` | `BehaviorSubject` for plain state |
| Component inputs | `input()`, `input.required()` | `@Input()` decorator |
| Component outputs | `output()` | `@Output() new EventEmitter` |
| Two-way binding | `model()` | manual `@Input()`+`@Output()` pair |
| Query children | `viewChild()`, `contentChild()` signal queries | `@ViewChild()` decorator |
| Reset state on input change | `linkedSignal(() => src())` | `effect()` that writes a signal |
| Async data → signals | `resource()` / `httpResource()` | manual `subscribe` + state flags |
| Defer heavy/below-fold UI | `@defer (on viewport)` | always eager-loading the chunk |
| Inject dependencies | `inject(Service)` | constructor params (in fns/base classes) |
| Conditionals/loops | `@if` / `@for` / `@switch` | `*ngIf` / `*ngFor` / `*ngSwitch` |
| List rendering | `@for (x of xs; track x.id)` | `@for` without `track` |
| Change detection | `ChangeDetectionStrategy.OnPush` | default (checks everything) |
| Observable in template | `async` pipe | manual `.subscribe()` in component |
| Stream teardown | `takeUntilDestroyed()` | unmanaged subscriptions |
| Update signal | `.set()` / `.update()` | mutating the value in place |

## Core Patterns

**Signal inputs/outputs over decorators** — reactive, typed, no lifecycle gymnastics:
```ts
// ❌ decorator inputs: not reactive, need ngOnChanges to derive
@Input() name = '';
@Output() saved = new EventEmitter<string>();
// ✅ signal inputs compose with computed; output() is leaner
name = input.required<string>();
upper = computed(() => this.name().toUpperCase());
saved = output<string>();
```
> Runnable: [`examples/signal-inputs-outputs.ts`](./examples/signal-inputs-outputs.ts)

**`inject()` over constructor injection** — works in functions, base classes, and factories:
```ts
// ❌ verbose, can't be used outside a constructor
constructor(private http: HttpClient, private route: ActivatedRoute) {}
// ✅
private http = inject(HttpClient);
private route = inject(ActivatedRoute);
```

**New control flow with mandatory `track`** — `@for` without `track` won't compile:
```html
<!-- ❌ structural-directive soup, no key -->
<div *ngFor="let u of users"><span *ngIf="u.active">{{ u.name }}</span></div>
<!-- ✅ block syntax, stable identity, built-in empty state -->
@for (u of users(); track u.id) {
  @if (u.active) { <span>{{ u.name }}</span> }
} @empty { <p>No users</p> }
```
> Runnable: [`examples/control-flow.ts`](./examples/control-flow.ts) (the block in a `@Component` template)

**OnPush + signals** — reading a signal in the template registers it as a dependency; updating it schedules a re-render with no manual `markForCheck()`. This is exactly the model zoneless (default in v21+) relies on, so `OnPush` everywhere makes a codebase zoneless-ready. Don't call functions in templates (they run every CD cycle); expose a `computed()` instead:
```ts
// ❌ filtered() runs on every change-detection pass
get filtered() { return this.items.filter(i => i.active); }
// ✅ recomputes only when items() changes
filtered = computed(() => this.items().filter(i => i.active));
```

**RxJS for async, signals for state** — interop at the boundary, never subscribe-in-subscribe:
```ts
// ❌ leaks (no teardown) + nested subscribe
this.route.params.subscribe(p =>
  this.http.get(`/u/${p['id']}`).subscribe(u => this.user = u));
// ✅ flatten with switchMap, auto-unsubscribe, expose as signal
user = toSignal(this.route.params.pipe(
  switchMap(p => this.http.get<User>(`/u/${p['id']}`)),
  takeUntilDestroyed(),
));
```
> Runnable: [`examples/rxjs-to-signal.ts`](./examples/rxjs-to-signal.ts)

**`resource()` for async reads, `linkedSignal()` for resettable derived state** — both stable (v22 / v20):
```ts
// reactive async: re-fetches when userId() changes, cancels stale loads, exposes signals
user = resource({ params: () => ({ id: this.userId() }), loader: ({ params }) => fetchUser(params.id) });
// in template: @if (user.isLoading()) {...} @else { {{ user.value()?.name }} }

// linkedSignal: derived BUT writable — resets to first option when options change,
// yet the user can still .set() a choice. computed() can't be written; an effect() would be a hack.
selected = linkedSignal(() => this.options()[0]);
```
> Runnable: [`examples/resource-linked-signal.ts`](./examples/resource-linked-signal.ts)

**`@defer` to shrink the initial bundle** — lazy-load a component's chunk on a trigger, no router needed:
```html
@defer (on viewport) {
  <app-heavy-chart [data]="data()" />
} @placeholder { <app-skeleton /> } @loading (after 100ms) { <app-spinner /> } @error { <p>Failed</p> }
```
> Runnable: [`examples/defer.ts`](./examples/defer.ts)

Triggers: `idle` (default), `viewport`, `interaction`, `hover`, `timer(…)`, `immediate`, `when <expr>`. Add `prefetch on hover` to warm the chunk early.

## Common Mistakes

- **NgModules for new code** — standalone is the default; only touch modules for legacy interop.
- **Manual subscriptions without teardown** — memory leaks. Prefer `async` pipe / `toSignal`; otherwise `takeUntilDestroyed()`.
- **Function calls / getters in templates** — re-run every CD cycle. Move to `computed()`.
- **Mutating signal values** — `arr().push(x)` won't notify. Use `.update(a => [...a, x])` / `.set()`.
- **`*ngFor` without `trackBy`** (or `@for` without `track`) — destroys/recreates DOM, breaks animations and focus.
- **Decorator inputs in new code** — use `input()` so values flow into `computed`/`effect`.
- **`effect()` for derived state** — use `computed()` (read-only) or `linkedSignal()` (writable); reserve `effect()` for side effects (logging, DOM, non-Angular APIs).
- **Relying on `zone.js` in v21+** — it's no longer the default. Avoid patterns that assume Zone auto-detects changes (e.g. mutating fields outside signals after a `setTimeout`); drive UI from signals/`async` pipe instead.

## When NOT to over-engineer

Not everything needs a signal. A value computed once and never reassigned is a plain `const`. Reach for RxJS only when you have real async/event streams (debounce, retry, combineLatest) — a single HTTP call piped to `toSignal` (or wrapped in `httpResource`) is fine; a `Subject` to model a boolean isn't. Keep `NgModule` only where a third-party library still requires it.

A copy-pasteable, compilable reference component lives in [`patterns.ts`](./patterns.ts): signal `input()`/`output()`/`model()`, `computed()`, `linkedSignal()`, `inject()`, `resource()`, and a `takeUntilDestroyed()` stream — each annotated with *why*.

## Sources

- [Signals overview](https://angular.dev/guide/signals) — `signal`/`computed`/`effect`
- [Dependent state with `linkedSignal`](https://angular.dev/guide/signals/linked-signal)
- [Async with `resource`](https://angular.dev/guide/signals/resource) and [`resource` API](https://angular.dev/api/core/resource) (stable v22)
- [Zoneless change detection](https://angular.dev/guide/zoneless) (default v21+)
- [`@defer` deferrable views](https://angular.dev/guide/templates/defer)
- [Versioning and releases](https://angular.dev/reference/releases) (v22 current as of 2026-06)
