---
name: angular-expert
description: Use when writing, reviewing, or refactoring Angular — standalone components, signals, RxJS streams, change detection, or dependency injection with inject(), and new control flow (@if/@for/@switch).
---

# Angular Expert

## Overview

Modern Angular (v17–19) is a different framework from the NgModule era. State lives in **signals**, components are **standalone**, DI uses the **`inject()`** function, and templates use **`@if`/`@for`/`@switch`**. New code that reaches for `NgModule`, `@Input()` decorators, or `*ngFor` is already legacy. These are the choices the CLI scaffolder won't always make for you.

## Quick Reference

| Goal | Do | Avoid |
|------|----|----|
| Component packaging | `standalone: true` (default v17+) | `NgModule` declarations |
| Local/derived state | `signal()`, `computed()` | `BehaviorSubject` for plain state |
| Component inputs | `input()`, `input.required()` | `@Input()` decorator |
| Component outputs | `output()` | `@Output() new EventEmitter` |
| Two-way binding | `model()` | manual `@Input()`+`@Output()` pair |
| Query children | `viewChild()`, `contentChild()` signal queries | `@ViewChild()` decorator |
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
@Component({ selector: 'app-greet' })
export class Greet {
  @Input() name = '';
  @Output() saved = new EventEmitter<string>();
}
// ✅ signal inputs compose with computed; output() is leaner
@Component({ selector: 'app-greet', standalone: true })
export class Greet {
  name = input.required<string>();
  upper = computed(() => this.name().toUpperCase());
  saved = output<string>();
}
```

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

**OnPush + signals** — reading a signal in the template registers it; mutation triggers re-render with no `markForCheck()`. Don't call functions in templates (they run every CD cycle); expose a `computed()` instead:
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

## Common Mistakes

- **NgModules for new code** — standalone is the default; only touch modules for legacy interop.
- **Manual subscriptions without teardown** — memory leaks. Prefer `async` pipe / `toSignal`; otherwise `takeUntilDestroyed()`.
- **Function calls / getters in templates** — re-run every CD cycle. Move to `computed()`.
- **Mutating signal values** — `arr().push(x)` won't notify. Use `.update(a => [...a, x])` / `.set()`.
- **`*ngFor` without `trackBy`** (or `@for` without `track`) — destroys/recreates DOM, breaks animations and focus.
- **Decorator inputs in new code** — use `input()` so values flow into `computed`/`effect`.
- **`effect()` for derived state** — use `computed()`; reserve `effect()` for side effects (logging, DOM, non-Angular APIs).

## When NOT to over-engineer

Not everything needs a signal. A value computed once and never reassigned is a plain `const`. Reach for RxJS only when you have real async/event streams (debounce, retry, combineLatest) — a single HTTP call piped to `toSignal` is fine; a `Subject` to model a boolean isn't. Keep `NgModule` only where a third-party library still requires it.
