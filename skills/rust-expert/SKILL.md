---
name: rust-expert
description: Use when writing, reviewing, or refactoring Rust — ownership/borrowing vs reflexive clone(), error handling with Result/? and thiserror vs anyhow, avoiding unwrap()/expect() in production, traits & generics vs dyn, lifetimes as a design signal, Option/Result combinators, and isolating unsafe.
---

# Rust Expert

## Overview

Idiomatic Rust is **borrow before you clone, encode errors in the type, and make illegal states unrepresentable.** The compiler enforces memory and thread safety; your job is the design it can't check. Most real churn in a Rust codebase isn't fighting the type system — it's `clone()` sprinkled to silence the borrow checker, `unwrap()` on genuinely fallible paths, and `dyn Trait` reached for where a generic fits cleanly. These are the judgment calls a linter can't make for you.

## Quick Reference

| Goal | Do | Avoid |
|------|----|----|
| Pass data to a function | borrow (`&T`, `&[T]`, `&str`) | take owned `T`/`Vec`/`String` then clone in |
| Quiet the borrow checker | restructure scopes/split borrows | reflexive `.clone()` to dodge it |
| Recover from failure | return `Result<T, E>`, propagate with `?` | `unwrap()`/`expect()` on fallible paths |
| Define a library error | `enum` impl `Error` (or `thiserror`) | `Box<dyn Error>` as your public API |
| Aggregate app errors | `anyhow::Result` + `.context()` | hand-rolled enums in a binary's `main` |
| Abstract over types | generic `<T: Trait>` bound | `dyn Trait` when the type is known statically |
| Heterogeneous collection | `Vec<Box<dyn Trait>>` | generics (can't hold mixed types) |
| Handle `Option`/`Result` | `map`/`and_then`/`unwrap_or_else` | deeply nested `match` |
| Reach for `unsafe` | tiny module with a safe wrapper + `// SAFETY:` | scattered `unsafe` blocks |
| Model state | distinct variants/types | a bool/`Option` soup that allows nonsense |

## Borrow before you reflexively clone

Default to borrowing: take `&str` not `String`, `&[T]` not `Vec<T>`, and return borrows tied to an input lifetime when you can. A `.clone()` is sometimes the right call (cheap `Copy` types, escaping a borrow conflict deliberately, `Arc::clone` for shared ownership) — but reaching for it the instant the borrow checker complains usually means the real fix is restructuring: shorten a borrow's scope, split a struct so fields borrow independently, or take `&mut` and mutate in place instead of consume-and-return. See [examples/ownership.rs](examples/ownership.rs).

```rust
// ❌ forces every caller to own a Vec, then clones again inside
fn first(items: Vec<String>) -> String { items[0].clone() }
// ✅ borrow in, borrow out — zero allocations
fn first(items: &[String]) -> Option<&str> { items.first().map(String::as_str) }
```

## Result, `?`, and thiserror (lib) vs anyhow (app)

Model fallibility in the type: return `Result<T, E>` and let `?` propagate, converting through `From` as it unwinds. For a **library**, define a concrete error enum so callers can match on variants — `thiserror` derives `Display`/`Error`/`From` for you, but a hand-written `impl Error` is the same shape (see [examples/errors.rs](examples/errors.rs)). For an **application** or binary, where you just need a rich message and a backtrace, `anyhow::Result<T>` with `.context("doing X")` is the pragmatic choice — don't make callers match errors they'll only print. The rule of thumb: thiserror when someone programmatically inspects the error, anyhow when a human reads it.

## No `unwrap()`/`expect()` on fallible paths

`unwrap()` and `expect()` turn a recoverable error into a panic — fine in tests, examples, and prototypes, dangerous in a service that should degrade gracefully. In production code, propagate with `?` or handle explicitly with `unwrap_or`, `unwrap_or_else`, or a `match`. Reserve panics for genuine invariant violations ("this slice is non-empty by construction"), and even then prefer `expect("why this can't fail")` so the message documents the assumption. `unwrap()` on `Option` from indexing or `HashMap::get` is a frequent crash source — use `?` (via `ok_or`) or a combinator instead.

## Generics + trait bounds vs `dyn Trait`

Prefer static dispatch: a generic `fn parse<R: Read>(r: R)` is monomorphized, inlinable, and zero-cost. Reach for `dyn Trait` (trait objects) only when you genuinely need *runtime* heterogeneity — a `Vec<Box<dyn Draw>>` of mixed concrete types, a plugin boundary, or to cut compile-time/binary bloat from excessive monomorphization. `impl Trait` in argument and return position covers the common "I just want to abstract over one type" case without naming it. Don't use a trait object to "keep it flexible" when every call site knows the concrete type — that's a vtable indirection bought for nothing.

```rust
fn total(shapes: &[Box<dyn Shape>]) -> f64 { shapes.iter().map(|s| s.area()).sum() } // needs dyn: mixed types
fn area(s: &impl Shape) -> f64 { s.area() } // static dispatch, one type, zero cost
```

## Lifetimes as a design signal

Lifetime annotations describe relationships the compiler already tracks; most functions need none thanks to elision. When you find yourself fighting lifetimes — especially storing a borrow inside a long-lived struct, or returning a reference that outlives its source — treat it as a signal that an ownership boundary is misplaced, not as a puzzle to annotate your way out of. Often the cleaner answer is to own the data (store `String`, not `&str`), use `Arc`/`Rc` for genuine shared ownership, or use an index/id instead of a back-reference. A struct full of lifetime parameters is usually telling you it's holding borrows it should own.

## `Option`/`Result` combinators over nested match

For transforming and chaining, combinators read better than pyramids of `match`: `map`, `and_then`, `or_else`, `unwrap_or_else`, `ok_or`, `?`, and `if let`/`let ... else` for early returns. Reserve `match` for cases where you genuinely branch on several variants with distinct logic. See `display_name` in [examples/errors.rs](examples/errors.rs).

```rust
// ❌ nested match noise
let name = match find(id) { Some(u) => match u.name { Some(n) => n, None => "?".into() }, None => "?".into() };
// ✅ combinator chain
let name = find(id).and_then(|u| u.name).unwrap_or_else(|| "?".into());
```

## Isolate `unsafe`

`unsafe` doesn't disable the borrow checker; it lets you do five specific things (deref raw pointers, call unsafe fns, etc.) whose invariants *you* now guarantee. Keep it in the smallest possible module behind a safe API, and document every block with a `// SAFETY:` comment stating why the invariant holds. The goal is that the rest of the codebase — and reviewers — only audit a tiny, clearly-marked surface, not chase soundness through scattered blocks. If you can express it safely (slices, iterators, `Cell`/`RefCell`), do that instead.

## Common Mistakes

- **Reflexive `.clone()`** to silence a borrow error — restructure the borrow first.
- **Owned params** (`String`/`Vec<T>`) where `&str`/`&[T]` would do — forces allocation on callers.
- **`unwrap()`/`expect()`** on I/O, parsing, or map lookups in production — propagate with `?`.
- **`Box<dyn Error>` as a library's public error type** — give callers an enum they can match.
- **`dyn Trait` where the concrete type is known** — pay no vtable cost; use a generic or `impl Trait`.
- **Lifetime-parameter soup in structs** — usually means it should own the data or use `Arc`/an id.
- **Nested `match` on `Option`/`Result`** — reach for combinators and `?`.
- **Scattered `unsafe`** without `// SAFETY:` notes — concentrate it behind a safe wrapper.
- **Stringly-typed state** (bools/`Option`s that allow impossible combinations) — encode it as an enum.

## When NOT to over-engineer

A script, test, or throwaway prototype is allowed to `unwrap()` and `clone()` freely — the discipline above is for production code that must not panic and runs hot. Don't add lifetimes, generics, or trait abstractions speculatively; introduce them when a second concrete type, a real performance need, or an actual API boundary appears. A little duplication or one well-placed `clone` is cheaper than a wrong abstraction. The standard library is the style guide — read how `std::io`, `Result`, and `Iterator` are shaped and imitate their restraint.

## Sources

- [The Rust Book](https://doc.rust-lang.org/book/) — ownership, error handling, generics, traits, lifetimes
- [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/)
- [Error Handling in Rust](https://doc.rust-lang.org/book/ch09-00-error-handling.html) · [thiserror](https://docs.rs/thiserror) · [anyhow](https://docs.rs/anyhow)
- [The Rustonomicon](https://doc.rust-lang.org/nomicon/) — `unsafe` and its invariants
- [Rust API Guidelines: dyn vs generics](https://rust-lang.github.io/api-guidelines/flexibility.html)
