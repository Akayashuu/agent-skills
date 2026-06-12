---
name: php-expert
description: Use when writing, reviewing, or refactoring PHP (8.1+) — modelling data with enums/readonly value objects, choosing match over switch, designing exceptions vs result types, wiring PSR interfaces & Composer autoloading, or tightening types for PHPStan.
---

# PHP Expert

## Overview

Modern PHP (8.1+) is statically-mindful and immutable-by-default when you let it be. The judgment is in **making invalid states unconstructable** — readonly value objects validated in their constructor, backed enums instead of loose constants, `match` instead of fall-through `switch` — and in depending on PSR *interfaces* rather than concrete libraries. The runtime is forgiving; PHPStan at level max is where the design pressure comes from. These are calls a linter alone won't make for you.

## Quick Reference

| Goal | Do | Avoid |
|------|----|----|
| Closed set of values | backed/pure `enum` | class `const` soup, magic strings |
| Immutable data | `public readonly` promoted props | setters / mutable DTOs |
| Branch on a value, return | `match` (===, expression) | `switch` (loose ==, fall-through) |
| Expected failure (parse/lookup) | union return `Ok\|Err` | exceptions for control flow |
| Truly exceptional condition | throw a typed `\Exception` | error codes / `false` sentinels |
| Reach a method as a callable | `$obj->m(...)` first-class syntax | `[$obj, 'm']` / `Closure::fromCallable` |
| Self-documenting call site | named arguments | positional bool/`null` flags |
| Function that always exits | `: never` return type | `: void` + implicit return |
| Optional chain | nullsafe `$a?->b?->c` | nested `if ($a !== null)` ladders |
| Depend on a collaborator | PSR interface (`LoggerInterface`) | a concrete class (`Monolog\Logger`) |
| Fake generics | `@template` docblock | `mixed` everywhere with no `@var` |
| Suppress a warning | fix the cause / check first | `@` error-suppression operator |
| File of definitions | `declare(strict_types=1);` at top | relying on type juggling |

## Core Patterns

**Readonly value object + enum — invalid instances can't exist.** Validate in the constructor; "mutation" returns a new instance. Implement `Stringable` for a clean cast.
```php
final class Money implements Stringable {
    public function __construct(
        public readonly int $amountMinor,   // cents, never floats for money
        public readonly Currency $currency, // backed enum
    ) {
        if ($amountMinor < 0) throw new InvalidArgumentException('negative');
    }
}
```
> Runnable: [`examples/value-object.php`](./examples/value-object.php)

**Compatibility gotcha:** `public readonly` *promoted properties* work in **8.1**, but the class-level `readonly class Foo {}` shorthand is **8.2+**. If you target 8.1, mark each property — don't reach for `readonly class`.

**Result type for expected failures — `match` forces both arms.** Reserve exceptions for the exceptional; a parse miss is not exceptional, so return it.
```php
/** @return Ok<int>|Err */
function parsePositiveInt(string $raw): Ok|Err { /* … */ }
```
> Runnable: [`examples/result-type.php`](./examples/result-type.php)

**`match` over `switch`.** Strict `===`, no fall-through, it's an expression, and an unmapped value throws `\UnhandledMatchError` instead of silently doing nothing. Over a pure enum, PHPStan flags a missing arm at analysis time. Use `: never` for the always-throwing helper so flow analysis knows the branch terminates.
```php
$idempotent = match ($method) {
    HttpMethod::Get, HttpMethod::Put, HttpMethod::Delete => true,
    HttpMethod::Post => false,
};
```
> Runnable: [`examples/match-exhaustive.php`](./examples/match-exhaustive.php)

**Program to a PSR interface, not an implementation.** Type-hint `LoggerInterface` (PSR-3), `RequestInterface` (PSR-7), `ContainerInterface` (PSR-11), `ClientInterface` (PSR-18) — any conforming library or test double drops in. And **never let fire-and-forget analytics throw**: swallow `\Throwable` at the edge so tracking can't break the request. The first-class callable `$obj->track(...)` captures the method without a wrapper lambda.
```php
public function __construct(private readonly LoggerInterface $log) {}
public function track(string $event, array $props = []): void {
    try { $this->log->info("event:$event", $props); }
    catch (\Throwable) { /* analytics must not affect control flow */ }
}
```
> Runnable: [`examples/psr-discovery.php`](./examples/psr-discovery.php)

**Generics via docblock.** PHP has no native generics; encode them with `@template` so PHPStan checks element types. Named arguments document the call site.
```php
/** @template T */
final class TypedStack {
    /** @param T $item */ public function push(mixed $item): void { /* … */ }
    /** @return T */      public function pop(): mixed { /* … */ }
}
/** @var TypedStack<string> $s */
```
> Runnable: [`examples/template-generics.php`](./examples/template-generics.php)

## Common Mistakes

- **Class constants for a closed set** — `const STATUS_ACTIVE = 1` carries no type and no exhaustiveness. Use a backed enum; you get `::cases()`, `::from()`, and methods.
- **`switch` for value branching** — loose `==`, accidental fall-through on a missing `break`, and it's a statement not an expression. Prefer `match`.
- **Exceptions as control flow / `false` sentinels** — a function returning `User|false` forces `=== false` checks and loses the failure reason. Return a typed result for *expected* failures; throw only for the exceptional.
- **`@` error suppression** — it hides the warning *and* its cause, and survives into production. Check the precondition (`isset`, `is_file`) or let it throw.
- **`mixed` plus `@var` casts to silence PHPStan** — `mixed` disables checking and `/** @var X */` is an unchecked claim. Narrow with `instanceof`/`is_*` or model the type. At level max these are smells, not fixes.
- **No `declare(strict_types=1);`** — without it `"7" == 7` and `f(int $x)` coerces silently. Put it at the top of every file.
- **Nullsafe to paper over a null that shouldn't exist** — `?->` is for genuinely optional chains, not for dodging a missing-data bug. Fix the type if it's never supposed to be null.
- **Reaching for `readonly class`** — fine on 8.2+, a fatal parse error on 8.1. Know your floor.

## When NOT to over-engineer

A `Result` type, `@template` generics, and deeply factored value objects have a readability cost. Reach for them when they prevent a class of real bugs — a public parser, a shared collection, money. For a private one-off transform, a plain typed function with a thrown exception is clearer than a hand-rolled `Ok|Err`. Don't add a PSR interface for a collaborator that will only ever have one implementation inside the same module.

## Sources

- [PHP Manual — Enumerations](https://www.php.net/manual/en/language.enumerations.php) · [readonly properties](https://www.php.net/manual/en/language.oop5.properties.php#language.oop5.properties.readonly-properties) · [match](https://www.php.net/manual/en/control-structures.match.php) · [first-class callable syntax](https://www.php.net/manual/en/functions.first_class_callable_syntax.php) · [`never`](https://www.php.net/manual/en/language.types.never.php) · [nullsafe operator](https://www.php.net/manual/en/language.oop5.basic.php#language.oop5.basic.nullsafe)
- [PHP 8.2 — readonly classes](https://www.php.net/releases/8.2/en.php) — the 8.1-vs-8.2 caveat
- [PSR-4 Autoloading](https://www.php-fig.org/psr/psr-4/) · [PSR-12 Coding Style](https://www.php-fig.org/psr/psr-12/) · [PSR-3 Logger](https://www.php-fig.org/psr/psr-3/) · [PSR-7 HTTP Message](https://www.php-fig.org/psr/psr-7/) · [PSR-11 Container](https://www.php-fig.org/psr/psr-11/) · [PSR-18 HTTP Client](https://www.php-fig.org/psr/psr-18/)
- [PHPStan — Rule Levels](https://phpstan.org/user-guide/rule-levels) · [PHPStan Generics](https://phpstan.org/blog/generics-in-php-using-phpdocs)
- [Composer — Autoloading](https://getcomposer.org/doc/04-schema.md#autoload)
