---
name: astro-expert
description: Use when building or debugging Astro sites — adding islands and client directives, choosing hydration timing, wiring content collections, handling SSR, or fixing View Transitions / ClientRouter, broken scripts, or state lost on navigation.
---

# Astro Expert

## Overview

Astro ships **zero JS by default** and renders components to HTML on the server. Interactivity is opt-in: you hydrate a single component (an *island*) only where the page needs it. The common mistake is treating Astro like a SPA and hydrating everything. Idiomatic Astro: server-render the page, then pay for JS one island at a time, choosing the laziest hydration that works.

## Quick Reference

| Goal | Do | Avoid |
|------|----|----|
| Static content | plain `.astro`, no directive | wrapping in a React/Vue island |
| Hydrate an interactive island | laziest directive that works | `client:load` everywhere |
| Below-the-fold widget | `client:visible` | `client:load` |
| No SSR-able output (uses `window`) | `client:only="react"` (sparingly) | forcing SSR then guarding `window` |
| Browser code in a component | `<script>` (bundled, resolves imports) | `<script is:inline>` for bare imports |
| Server → island data | serializable `props` | passing functions/class instances |
| Typed markdown/MDX | content collections + Zod schema | raw `fs`/`import.meta.glob` |
| Re-run JS after View Transition nav | `astro:page-load` listener | `DOMContentLoaded` only |
| Keep DOM/state across nav | `transition:persist` | re-mounting + restoring manually |

## Core Patterns

**Client directives are a cost ladder — pick the laziest that works:**
```astro
---
import Counter from '../components/Counter.tsx'
---
<!-- ❌ hydrates immediately, blocks main thread, even off-screen -->
<Counter client:load />
<!-- ✅ hydrates only when scrolled into view -->
<Counter client:visible />
```
`client:idle` (after first paint), `client:media="(max-width: 50em)"` (only when the query matches), and `client:only="react"` (skips SSR — use only when the component can't render on the server) round out the ladder.

**`<script>` is bundled; `<script is:inline>` is not** — bare imports only resolve in the processed form:
```astro
<!-- ❌ is:inline is shipped verbatim; the browser can't resolve a bare specifier -->
<script is:inline>
  import { animate } from 'motion' // fails in browser
</script>
<!-- ✅ Astro bundles this, resolves imports, dedupes across the page -->
<script>
  import { animate } from 'motion'
  animate('#hero', { opacity: 1 })
</script>
```

**Pass server data to islands as serializable props** (`define:vars` is for `<style>`/inline scripts only):
```astro
---
const user = await getUser()
---
<!-- ❌ functions/class instances/Dates-with-methods don't survive serialization -->
<Profile client:visible user={user} onSave={() => save(user)} />
<!-- ✅ plain serializable data; do the wiring inside the island -->
<Profile client:visible user={{ id: user.id, name: user.name }} />

<!-- define:vars exposes server values to a NON-bundled inline script -->
<style define:vars={{ accent: user.color }}>a { color: var(--accent) }</style>
```

**Content collections — type-safe frontmatter over globbing:**
```ts
// src/content.config.ts
import { defineCollection, z } from 'astro:content'
const blog = defineCollection({
  schema: z.object({ title: z.string(), pubDate: z.date(), draft: z.boolean().default(false) }),
})
export const collections = { blog }
```
```astro
---
import { getCollection } from 'astro:content'
const posts = await getCollection('blog', ({ data }) => !data.draft) // data is fully typed
---
```

**View Transitions re-run module scripts but not always your listeners.** With `<ClientRouter />`, navigation swaps the DOM in place — `DOMContentLoaded` fires once, so init code tied to it won't re-run:
```astro
---
import { ClientRouter } from 'astro:transitions'
---
<head><ClientRouter /></head>
<!-- ❌ runs once, breaks after the first client-side nav -->
<script>document.addEventListener('DOMContentLoaded', init)</script>
<!-- ✅ fires on initial load AND every transition -->
<script>document.addEventListener('astro:page-load', init)</script>
<!-- keep a player/sidebar mounted across navigations -->
<aside transition:persist><audio controls /></aside>
```

## Common Mistakes

- **`client:load` on everything** — defeats Astro's whole model; the page now ships a SPA. Default to no directive, escalate to `client:visible`/`client:idle`, reserve `client:load` for above-the-fold interactive UI.
- **Bare imports in `is:inline` scripts** — they ship unprocessed and fail in the browser. Drop `is:inline` to get bundling and import resolution.
- **`DOMContentLoaded` with `<ClientRouter />`** — listen to `astro:page-load` (every nav) and `astro:after-swap` (right after DOM swap) instead.
- **Non-serializable island props** — functions, class instances, and other live objects can't cross the server→client boundary. Pass data, do behavior inside the island.
- **Fetching in the client** that could run server-side — frontmatter runs on the server with no bundle cost and no loading spinner; prefer it unless the data is user-specific and live.
- **`Astro.params` vs `Astro.props`** — `params` come from the file-based route (`[slug].astro`), `props` from `getStaticPaths`/the parent. Don't read route data off the URL manually.

## When NOT to over-engineer

If a page is content with no interactivity, ship plain `.astro` and **no framework** — don't pull in React just for a layout. Don't add `<ClientRouter />` for SPA feel on a site that's fine as an MPA; the default full-page nav is fast and free. Reach for `client:only` only when SSR genuinely can't run the component, not to avoid a hydration warning. The framework's value is shipping less JS — every directive you add spends that budget.
