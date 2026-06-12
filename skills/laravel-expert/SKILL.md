---
name: laravel-expert
description: Use when building or reviewing Laravel apps or packages — service providers, container bindings, Eloquent/N+1, form requests, queued jobs, events, config vs env, facades vs DI, or Testbench/Pest tests.
---

# Laravel Expert

## Overview

Idiomatic Laravel leans on the framework's conventions — the container, providers, Eloquent — instead of fighting them, while staying explicit where implicit magic becomes a footgun (mass assignment, `env()` after caching, N+1). These are the judgment calls that separate a clean package or app from one that leaks queries and stale config. This skill is written from the **package-author** perspective: most rules apply to apps too, but provider wiring, auto-discovery, publishing, and Testbench are where packages differ.

## Quick Reference

| Goal | Do | Avoid |
|------|----|----|
| Read configuration at runtime | `config('x.y')` | `env('X')` outside `config/*.php` (returns `null` when config is cached) |
| Bind an interface | `bind`/`singleton` in `register()` | resolving other services in `register()` |
| Same instance everywhere | `singleton` | `bind` (new instance per resolve) when state/connection is shared |
| Register routes/migrations/publish | `boot()` | doing it in `register()` |
| Ship a package provider | `extra.laravel.providers` auto-discovery | telling users to edit `config/app.php` |
| Merge package config | `mergeConfigFrom` (shallow, user wins) | overwriting the published config |
| Read request input | `$request->validated()` from a Form Request | `$request->all()` into `Model::create()` |
| Mass-assignment safety | explicit `$fillable` allow-list | `$guarded = []` |
| Load relations | `with([...])` / `withCount` (eager) | lazy access in a loop (N+1) |
| Background work | `ShouldQueue` + idempotent `handle()` | assuming a job runs exactly once |
| Cross-cutting hook | event + listener | fat controller calling everything inline |
| Need a fresh/decorated instance per call | inject the contract | a facade (harder to swap/mock per-call) |

## Core Patterns

**Service provider: `register` binds, `boot` wires.** `register()` may only put things into the container — never resolve another service there, it might not be registered yet. Everything that touches the booted framework (routes, migrations, publishing, views, listeners) goes in `boot()`. A provider can be **deferred** (`provides()` + no eager work in `register()`) so it only loads when one of its bindings is resolved.
```php
public function register(): void {
    $this->mergeConfigFrom(__DIR__.'/../config/package.php', 'package');
    $this->app->singleton(Reporter::class, HttpReporter::class);
}
public function boot(): void {
    $this->loadRoutesFrom(__DIR__.'/../routes/package.php');
    $this->publishes([__DIR__.'/../config/package.php' => config_path('package.php')], 'package-config');
}
```
> Runnable: [`examples/service-provider.php`](./examples/service-provider.php)

**Container: bind contracts, choose `singleton` vs `bind` deliberately.** `bind` gives a new instance every resolve; `singleton` gives one shared instance for the lifetime of the request/worker. Type-hinted dependencies are auto-resolved; use **contextual binding** (`when()->needs()->give()`) when one consumer needs a different implementation or a config-driven scalar.
```php
$this->app->when(HttpReporter::class)->needs('$timeout')->giveConfig('package.timeout');
```
> Runnable: [`examples/service-provider.php`](./examples/service-provider.php)

**Config over `env()` — the cached-config gotcha.** `php artisan config:cache` (standard in production) freezes config and **unsets `$_ENV` for app code**: any `env()` call outside a `config/*.php` file then returns `null`. Read env only inside config files; everywhere else read `config()`.

**Eloquent: explicit mass assignment, native casts, eager loading.** Prefer an explicit `$fillable` allow-list over `$guarded = []` (an empty guard makes every column settable from input). Push enum/date conversion into `casts()`. Encapsulate reusable filters in query scopes. Kill N+1 by eager-loading the relations you'll touch with `with()`/`withCount`; in dev, `Model::preventLazyLoading()` turns an accidental lazy load into a thrown error.
```php
$posts = Post::published()->with(['author', 'comments'])->withCount('comments')->get();
```
> Runnable: [`examples/eager-loading.php`](./examples/eager-loading.php)

**Form Requests: validate + authorize at the edge, read `validated()`.** Move `authorize()` and `rules()` out of the controller; the action only runs on valid, authorized input. Reading `$request->validated()` returns only the rule-listed subset, which is what you should hand to `create()`/`update()` — closing the hole that `$request->all()` opens.
> Runnable: [`examples/form-request.php`](./examples/form-request.php)

**Queued jobs must be idempotent.** Queues retry on failure (`$tries`, `$backoff`), so a job can run more than once. Make `handle()` safe under re-execution — claim state atomically (transaction + `lockForUpdate`) rather than trusting a "did we already do it" flag. Use `ShouldBeUnique` to avoid duplicate dispatch, `failed()` to compensate, and let `SerializesModels` re-fetch fresh model state instead of carrying a stale snapshot.
> Runnable: [`examples/queued-job.php`](./examples/queued-job.php)

**Events/listeners decouple side effects.** Emit a domain event (`OrderPaid`) and let listeners (email, ledger, webhook) react. Listeners can be queued (`implements ShouldQueue`) so slow side effects don't block the request. This keeps controllers thin and side effects independently testable.

**Facades vs dependency injection.** Facades are fine for framework globals in app code and read well (`Cache::get`). For your own collaborators — especially in package code and anything you want to swap or mock per call — **inject the contract** via the constructor: it's explicit, testable without `Facade::swap`, and works with contextual binding.

**Test packages with Testbench, apps with Pest/PHPUnit.** A package has no host app, so extend Orchestra Testbench's `TestCase` and register your provider via `getPackageProviders()`; it boots a minimal app so the container, config, and migrations behave realistically. App test suites instead extend the framework `TestCase` with `RefreshDatabase`.
> Runnable: [`examples/testbench-test.php`](./examples/testbench-test.php)

## Common Mistakes

- **`env()` outside config files** — returns `null` once `config:cache` runs. The bug only shows in production. Route every value through a `config/*.php` file.
- **Resolving services in `register()`** — order isn't guaranteed; the dependency may be unbound. Defer that work to `boot()` or a resolve-time closure.
- **`$guarded = []`** — a mass-assignment hole. Combine with `$request->all()` and an attacker sets `is_admin`. Use `$fillable` + `validated()`.
- **N+1 from lazy loading in loops** — accessing `$post->author` inside `foreach` fires a query per row. Eager load up front.
- **Assuming a job runs once** — retries, duplicate dispatch, and at-least-once delivery mean it may run twice. Design for idempotency.
- **`singleton` for stateful-per-request things** — sharing one instance across a queue worker's many jobs can leak state between jobs. Match lifetime to intent.
- **Editing `config/app.php` providers for a package** — use `extra.laravel.providers` auto-discovery instead; only the app's own providers belong there.
- **Overwriting published config in `boot()`** — use `mergeConfigFrom` (shallow merge) so the user's published values win.

## When NOT to over-engineer

Not every class needs an interface and a binding — bind a contract when you actually have (or will have) more than one implementation or need to mock it; otherwise inject the concrete. Don't queue a job that finishes in microseconds, don't add an event for a one-listener side effect you'll never reuse, and don't reach for a custom cast or repository layer when an Eloquent model and a scope already say it clearly. Convention first; abstraction only where it earns its weight.

## Sources

- [Service Container](https://laravel.com/docs/container) · [Service Providers](https://laravel.com/docs/providers) · [Facades](https://laravel.com/docs/facades)
- [Package Development](https://laravel.com/docs/packages) — auto-discovery, publishing, `mergeConfigFrom`
- [Configuration](https://laravel.com/docs/configuration#configuration-caching) — the `env()` / `config:cache` gotcha
- [Eloquent](https://laravel.com/docs/eloquent) · [Eager Loading / N+1](https://laravel.com/docs/eloquent-relationships#eager-loading) · [Mass Assignment](https://laravel.com/docs/eloquent#mass-assignment)
- [Validation / Form Requests](https://laravel.com/docs/validation#form-request-validation)
- [Queues](https://laravel.com/docs/queues) — `ShouldQueue`, unique jobs, failed jobs · [Events](https://laravel.com/docs/events)
- [Orchestra Testbench](https://packages.tools/testbench) · [Pest](https://pestphp.com/docs/installation)
