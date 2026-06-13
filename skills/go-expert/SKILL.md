---
name: go-expert
description: Use when writing, reviewing, or refactoring Go — error handling and wrapping (errors.Is/As, %w), goroutine/context cancellation and leaks, interfaces defined at the consumer, zero values vs constructors, slice/map aliasing, defer cost, and when NOT to reach for generics.
---

# Go Expert

## Overview

Idiomatic Go is **errors are values, share memory by communicating, and make the zero value useful.** The language is small on purpose: clarity beats cleverness, and the standard library is the model to imitate. Most real Go bugs are not type errors — they are leaked goroutines, swallowed or mis-wrapped errors, and interfaces abstracted one layer too early. These are the judgment calls a linter can't make for you.

## Quick Reference

| Goal | Do | Avoid |
|------|----|----|
| Add context to an error | `fmt.Errorf("...: %w", err)` | `fmt.Errorf("...: %v", err)` (drops the chain) |
| Match a sentinel error | `errors.Is(err, ErrNotFound)` | `err == ErrNotFound` (breaks on wrap) |
| Match a typed error | `errors.As(err, &target)` | type assertion on a wrapped err |
| Start a goroutine | give it a way to stop (`ctx`, closed chan) | fire-and-forget with no exit path |
| Time/cancel work | thread `context.Context` as first arg | `time.Sleep` polling, global flags |
| Define an interface | at the consumer, only methods it uses | big interface next to the implementation |
| Return a value | concrete struct | an interface "for flexibility" |
| New aggregate type | usable zero value (`var b bytes.Buffer`) | mandatory `NewX()` that only sets defaults |
| Subslice you'll `append` to | `slices.Clone` / 3-index slice first | append into a slice that aliases another |
| Reach for generics | a real type-parameterized algorithm | replacing one or two concrete types |

## Error wrapping & matching

Errors are ordinary values; return them, don't panic across package boundaries. Add context as the stack unwinds with `fmt.Errorf` and the `%w` verb — `%w` preserves the chain so callers can still match the cause; `%v` flattens it to a string and severs `Is`/`As`. Match by behavior, never by string or `==`: `errors.Is` for sentinels (`ErrNotFound`), `errors.As` for typed errors you need to inspect. Wrap at boundaries you own, but don't double-wrap noise — each layer should add one piece of context. See [examples/errors.go](examples/errors.go).

## Goroutine leaks & context

Every goroutine needs an exit path. A goroutine blocked forever on a channel send/receive is a leak the GC can't collect — the most common Go production bug. Thread `context.Context` as the first parameter through anything that blocks, does I/O, or spawns work, and guard every channel operation with a `select` on `ctx.Done()`. The launcher decides lifetime (`context.WithCancel`/`WithTimeout` + `defer cancel()`); the goroutine just honors cancellation. See [examples/concurrency.go](examples/concurrency.go).

```go
// ❌ leaks if no one ever receives
go func() { ch <- compute() }()
// ✅ also exits when the caller gives up
go func() {
	select {
	case ch <- compute():
	case <-ctx.Done():
	}
}()
```

For a bounded fan-out with error propagation, `errgroup.Group` (golang.org/x/sync) is the idiomatic tool — but the same `select`-on-`Done` discipline underlies it.

## Accept interfaces, return structs

Define interfaces where they're *consumed*, not where they're implemented, and keep them small — `io.Reader` is one method. A function should accept the narrowest interface it actually uses and return a concrete type, so callers keep full access and you don't pre-commit to an abstraction nobody needs. Premature interfaces (a `UserService` interface with a single implementation, declared next to that implementation) add indirection without buying decoupling. Introduce the interface when a second implementation or a test fake genuinely appears.

```go
// ✅ consumer-side, minimal: anything readable works, including a test buffer
func Count(r io.Reader) (int, error) { /* ... */ }
```

## Useful zero values vs needless constructors

Design types so the zero value is ready to use: `var mu sync.Mutex`, `var b bytes.Buffer`, and a `nil` slice all work immediately — no `New` required. A constructor earns its place only when it must establish an invariant (open a connection, validate, wire dependencies). A `NewThing` that just zero-fills fields is friction. Likewise, return `nil` for an empty slice rather than `[]T{}`; `len`, `range`, and `append` all handle `nil` correctly.

## Slice & map aliasing

A slice is a view (pointer, len, cap) over a backing array; copying the slice header doesn't copy the data. `append` may mutate the shared backing array in place when there's spare capacity, so two slices can silently clobber each other. When you hand out or retain a subslice you'll later grow, `slices.Clone` it, or use a 3-index slice `s[a:b:b]` to force `append` to allocate. Maps are reference types too — store a struct value and you can't mutate a field through the map; store a pointer or reassign the whole value.

```go
sub := slices.Clone(data[2:5]) // independent backing array; append won't touch data
```

## Generics — when NOT to use them

Generics are for genuinely type-parameterized *algorithms and containers* (`slices`, `maps`, an ordered tree, a `Min/Max`). They are not a substitute for interfaces, which model behavior, nor a reason to abstract code used at one or two concrete types. If a plain function, an interface, or a little duplication is clearer, prefer it — Go culture treats a bit of repetition as cheaper than the wrong abstraction. Reach for a type parameter only when you'd otherwise write the identical logic for several unrelated types and an interface can't express the constraint.

## Common Mistakes

- **`%v` instead of `%w`** when wrapping — silently severs `errors.Is`/`As`.
- **Comparing errors with `==`** or matching on `err.Error()` strings — breaks the moment someone wraps.
- **Goroutine with no exit path** — leaks when the receiver/sender disappears; always select on `ctx.Done()`.
- **Ignoring `context` cancellation** in loops and I/O — work runs after the caller has moved on.
- **Big interfaces beside the implementation** — define them small, at the consumer.
- **Mandatory constructors** for types whose zero value already works.
- **`defer` in a hot loop** — defers run at function return, not loop iteration; close explicitly inside the loop or refactor into a helper.
- **`append` onto an aliased slice** — clone or 3-index slice before growing a shared view.
- **`range` loop variable captured in a goroutine** — fixed in Go 1.22 (per-iteration scope), but be explicit when targeting older toolchains.

## When NOT to over-engineer

Small programs don't need layered packages, DI frameworks, or an interface per struct. Start concrete; add an interface when a real seam appears, a constructor when there's a real invariant, a goroutine when there's real concurrency to manage. The standard library is the style guide: read `io`, `net/http`, and `errors` and imitate their restraint.

## Sources

- [Effective Go](https://go.dev/doc/effective_go)
- [Error handling and Go](https://go.dev/blog/error-handling-and-go) · [Working with Errors in Go 1.13](https://go.dev/blog/go1.13-errors)
- [Go Concurrency Patterns: Context](https://go.dev/blog/context) · [Pipelines and cancellation](https://go.dev/blog/pipelines)
- [When To Use Generics](https://go.dev/blog/when-generics)
- [Go Code Review Comments](https://go.dev/wiki/CodeReviewComments)
