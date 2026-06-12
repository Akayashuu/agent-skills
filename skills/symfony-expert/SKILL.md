---
name: symfony-expert
description: Use when building or reviewing Symfony 6.4/7.x apps or bundles — wiring the DI container (autowiring, tags, #[Autowire], compiler passes), authoring a bundle Extension/Configuration, attribute routing, Twig extensions, events, HttpClient, or pinning component versions with Flex.
---

# Symfony Expert

## Overview

Idiomatic Symfony is about letting the container do the wiring and keeping decisions declarative. Autowiring + autoconfiguration + attributes replace almost all hand-written `services.yaml`; reach for a compiler pass or an explicit tag only when the framework genuinely can't infer the wiring. From the bundle-author seat the bar is higher: your `Extension`, `Configuration` tree, and `prepend` hook are a public contract, so they must validate input and set sane defaults rather than read globals. These are the judgment calls the framework can't make for you.

## Quick Reference

| Goal | Do | Avoid |
|------|----|----|
| Wire your own services | autowiring + autoconfiguration (zero config) | hand-listing every service in YAML |
| Pick one of several tagged services | `#[AsTaggedItem(index)]` + injected iterator/locator | manual `!tagged_iterator` plumbing |
| Inject a scalar/env into one service | `#[Autowire('%env(...)%')]` on the param | a global parameter just for one consumer |
| Current HTTP request inside a service | inject `RequestStack`, call `getCurrentRequest()` | injecting `Request` (stale / absent off-request) |
| React to a framework/app event | `#[AsEventListener]` | manual `kernel.event_listener` tag |
| Several events in one class | `EventSubscriberInterface` | many separate listeners |
| Bundle user config | `Configuration` tree + `Extension::load` | reading `$_ENV` in the Extension |
| Set defaults on another bundle | `prepend()` in your Extension | telling users to edit their config |
| Twig callable returning markup | `is_safe => ['html']` + escape input yourself | returning raw HTML without is_safe (double-escaped) |
| Pin a component version | `extra.symfony.require` (needs symfony/flex) | assuming it works in a flex-less CI matrix |
| HTTP calls | `HttpClientInterface` (PSR-18 via `Psr18Client`) | curl/file_get_contents |
| Modify definitions across bundles | a `CompilerPass` | doing it where load order isn't guaranteed |

## Core Patterns

**The bundle Extension — bridge between user config and the container.** The class MUST be named `<Alias>Extension`; `load()` validates config against the tree then loads `services.php`. Turn validated config into parameters or method calls — don't read env vars here. Use `prepend()` to set defaults on *other* bundles (Twig paths, an http_client scope) before they load.
```php
$config = $this->processConfiguration(new Configuration(), $configs);
$container->setParameter('acme_payment.api_key', $config['api_key']);
```
> Runnable: [`examples/di-extension.php`](./examples/di-extension.php)

**The Configuration tree — your bundle's validated, self-documenting config contract.** Root name MUST equal the Extension alias. `isRequired()`, `cannotBeEmpty()`, `enumNode()->values()`, `addDefaultsIfNotSet()` give users validation and `config:dump-reference` output for free.
> Runnable: [`examples/configuration-tree.php`](./examples/configuration-tree.php)

**RequestStack, never Request.** Services are shared singletons; the `Request` is per-request and simply absent in CLI/worker contexts. Injecting `Request` freezes a stale or missing object. Inject `RequestStack` and fetch the current request each call, tolerating `null`. Bind scalars at the injection point with `#[Autowire]` instead of inventing a global parameter.
```php
public function __construct(
    private RequestStack $requestStack,
    #[Autowire('%env(string:APP_LOCALE)%')] private string $defaultLocale = 'en',
) {}
```
> Runnable: [`examples/request-stack-service.php`](./examples/request-stack-service.php)

**Event listeners via attribute.** `#[AsEventListener(event: KernelEvents::RESPONSE, priority: -10)]` on an `__invoke`able class is autoconfigured — no tag. Subscribe by the `KernelEvents` constant (typo = fatal, not a silent no-op), and guard with `isMainRequest()` so sub-requests don't get double-processed. Use a subscriber only when one class owns several events.
> Runnable: [`examples/event-listener.php`](./examples/event-listener.php)

**Twig extension with html-safe output.** Autoconfiguration tags it automatically. A callable returning markup needs `is_safe => ['html']` or Twig double-escapes it — but that makes *you* responsible for `htmlspecialchars`-ing any interpolated input. `is_safe` over unescaped user input is an XSS hole.
```php
new TwigFunction('price_badge', $this->priceBadge(...), ['is_safe' => ['html']]);
```
> Runnable: [`examples/twig-extension.php`](./examples/twig-extension.php)

**Tagged services & selection.** Tag a family with an interface (autoconfigure maps interface → tag), then inject `#[TaggedIterator('app.handler')]` or a `ServiceLocator`. `#[AsTaggedItem(index: 'visa', priority: 10)]` keys/orders items so you can pick one by name without a compiler pass.

**Compiler pass — only when load order matters.** Use `process(ContainerBuilder)` to collect `findTaggedServiceIds()` and rewire definitions *after* all extensions have loaded. If the decision is purely config-driven, do it in `load()` instead — a pass is heavier and runs out of band.

**Attribute routing & controllers.** `#[Route('/pay/{id}', methods: ['POST'])]` on the action; type-hint services as action arguments (autowired per-action) and let `#[MapRequestPayload]` / `#[MapQueryString]` deserialize+validate input. Controllers extending `AbstractController` get `$this->json()`, `render()`, etc.; a plain invokable controller is fine too.

**HttpClient & PSR-18.** Inject `HttpClientInterface` (scoped clients via `framework.http_client.scoped_clients`, or `#[Target('acmePayment.http')]`). When a library needs a PSR-18 client, wrap it: `new Psr18Client($symfonyHttpClient)` — you keep Symfony's retry/profiler and still satisfy the PSR contract.

## Common Mistakes

- **Injecting `Request`, `Session`, or `Security`'s user into a service constructor** — all are request-scoped. Inject `RequestStack` / `Security` and read on demand.
- **Reading `$_ENV` / `getenv()` in a bundle Extension or service** — expose it as config or `%env()%` so it's overridable and cacheable. Env access in `load()` happens at compile time and gets baked into the cached container.
- **`is_safe => ['html']` without escaping interpolated input** — XSS. Escape everything you didn't generate.
- **Reaching for a compiler pass for config-driven wiring** — if you can decide in `load()` from the processed config, do that; passes are for cross-bundle, post-load rewiring.
- **`extra.symfony.require` in `composer.json` to pin a component, but no `symfony/flex` installed** — Flex is what reads that key. In a CI matrix that pins versions without flex, the constraint is silently ignored and you resolve the wrong versions. Either install flex or pin with real `require` constraints.
- **Subscribing to an event by string literal** — use the `*Events` constant; a typo'd string just never fires.
- **Forgetting `isMainRequest()`** in kernel.request/response listeners — sub-requests (fragments/ESI/error) re-trigger them.
- **`new` instead of the container** for things with dependencies — you lose autowiring, decoration, and lazy services.
- **Mismatched Extension alias and Configuration root** — config silently won't bind.

## When NOT to over-engineer

A small app does not need a bundle, a compiler pass, or hand-tuned service tags — autowiring + autoconfiguration with `services.yaml`'s default `resource:` glob covers it. Don't build a Configuration tree for two parameters you could `#[Autowire]` directly. Write the bundle Extension/Configuration machinery when you're actually distributing reusable code (e.g. a `takt-symfony` integration bundle), not for app-local services.

## Sources

- [Service Container](https://symfony.com/doc/current/service_container.html) · [Autowiring](https://symfony.com/doc/current/service_container/autowiring.html) · [`#[Autowire]` & service attributes](https://symfony.com/doc/current/service_container/autowiring.html#autowiring-other-services)
- [Bundles](https://symfony.com/doc/current/bundles.html) · [Bundle configuration & semantic config](https://symfony.com/doc/current/bundles/configuration.html) · [`prependExtension`](https://symfony.com/doc/current/bundles/prepend_extension.html)
- [Compiler passes](https://symfony.com/doc/current/service_container/compiler_passes.html) · [Service tags](https://symfony.com/doc/current/service_container/tags.html)
- [Events & EventDispatcher](https://symfony.com/doc/current/event_dispatcher.html) · [Kernel events](https://symfony.com/doc/current/reference/events.html)
- [Routing attributes](https://symfony.com/doc/current/routing.html) · [Twig extensions](https://symfony.com/doc/current/templates.html#creating-extensions)
- [HttpClient & PSR-18](https://symfony.com/doc/current/http_client.html#psr-18-and-psr-17) · [Symfony Flex & `extra.symfony.require`](https://symfony.com/doc/current/setup/flex.html)
- [Configuring with env vars & secrets](https://symfony.com/doc/current/configuration.html#configuration-based-on-environment-variables)
