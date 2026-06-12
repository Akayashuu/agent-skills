---
name: takt-expert
description: Use when integrating Takt analytics into a web app, or authoring/maintaining a @vskstudio/takt-* wrapper — covers init/pageview/track, the excludeLocalhost gotcha, SPA pageviews, sendBeacon transport, and per-framework idioms.
---

# Takt Expert

## Overview

Takt is a privacy-friendly, ≤1 kB analytics client. `@vskstudio/takt-core` is the engine; the official framework wrappers are thin, SSR-safe layers that **never change the wire payload or privacy logic**. Wrappers re-export core's behaviour and add native ergonomics (provider/hook/directive). Always pin a version in production.

## Quick Reference

| Target | Install | Boot |
|--------|---------|------|
| Core (any) | `@vskstudio/takt-core` | `init({ domain })` |
| React | `@vskstudio/takt-react @vskstudio/takt-core` | `<Takt domain>` + `useTakt()` |
| Vue 3 | `@vskstudio/takt-vue @vskstudio/takt-core` | `<Takt>` / `app.use(TaktPlugin)` + `useTakt()` |
| Svelte 5 | `@vskstudio/takt-svelte @vskstudio/takt-core` | `<Takt />` + `useTakt()` |
| Solid | `@vskstudio/takt-solid @vskstudio/takt-core` | `<Takt domain>` + `useTakt()` |
| Angular 17+ | `@vskstudio/takt-angular @vskstudio/takt-core` | `provideTakt({…})` + `inject(TaktService)` |
| Astro | `@vskstudio/takt-astro @vskstudio/takt-core` | `integrations: [takt({ domain })]` |

Core exports: `init`, `createTakt`, `track`, `pageview`, `optOut`, `optIn`, and types `Config`, `InitOptions`, `TrackOptions`.

## Core Patterns

**Init + the `excludeLocalhost` gotcha.** `init()` makes one shared instance, fires an automatic pageview, and wires SPA navigation. By default core **suppresses every event on localhost / private IPs** (and when Do Not Track is on, or the visitor opted out, or `sampleRate` drops it). During local dev you will see nothing until you flip it:

```ts
import { init, track, pageview } from '@vskstudio/takt-core'

init({ domain: 'example.com', outbound: true, files: true, excludeLocalhost: false })
```

For multiple instances or explicit teardown use the side-effect-free factory `createTakt()`; its `enableSpa()`/`enableOutbound()`/`enableFiles()` each return a disposer.

**Custom events & revenue.** Props are coerced to strings and capped (30 keys, 64-char keys, 1024-char values); revenue needs a well-formed amount and a 3-letter currency or it is dropped:

```ts
track('Signup', {
  props: { plan: 'pro' },
  revenue: { amount: '29.00', currency: 'EUR' },
})
```

**SPA pageviews** are automatic — `init()` (and every `<Takt>`/`provideTakt`) patches `pushState`/`replaceState` + `popstate`. Don't also call `pageview()` on route change or you double-count. Astro is the exception: its router replays history per navigation, so the Astro integration tracks `astro:after-swap` instead — never combine the integration and `<Takt />` component.

**Transport.** Every event POSTs compact JSON to `endpoint` (default `/api/event`) via `navigator.sendBeacon`, falling back to `fetch(..., { method: 'POST', keepalive: true })`. It never throws. Wire keys are frozen: `n` name, `d` domain, `u` url, `r` referrer, `w` width, `p` props, `$` revenue `{ a, c }`. URLs strip query + hash by default (opt back in via `trackQuery` / `queryParams` / `scrubUrl`).

## Common Mistakes

- **"No events in dev"** — that's `excludeLocalhost` (default `true`), not a bug. Set `excludeLocalhost: false` locally.
- **Manual `pageview()` per route** — SPA tracking is already on; you'll double-count.
- **Mutating config props after mount** — wrappers read config once at mount; remount to reconfigure.
- **Forgetting the core peer dep** — wrappers list `@vskstudio/takt-core` as a peer; install both.
- **Expecting query strings** — they're stripped by default; secrets in `?token=` never leave the browser.
- **Astro double-boot** — integration and `<Takt />` both boot the default instance; pick one.

## Authoring a wrapper checklist

- SSR-safe: touch `window`/`navigator` only after mount (`onMount`/mount effect/`isPlatformBrowser`); no-op on the server.
- `useTakt()` (or service) returns a **never-throwing no-op** before mount / during SSR.
- Pass config straight through to core; never reshape the payload or reimplement privacy/sampling.
- Mirror core option names exactly (`domain`, `endpoint`, `outbound`, `files`, `spa`, `respectDnt`, `excludeLocalhost`).
- Declare `@vskstudio/takt-core` (and the framework) as peer deps; ship ESM, tree-shakeable.
- Offer the framework-agnostic `<takt-analytics>` custom element for non-framework pages.
