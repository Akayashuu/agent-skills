# Takt — copy-paste setup per framework

Verified against each wrapper's published README/API. Every wrapper lists
`@vskstudio/takt-core` as a peer dep, so always install both. Privacy defaults
(`spa`/`respectDnt`/`excludeLocalhost`) are `true`; pass `excludeLocalhost={false}`
(or the framework equivalent) during local dev or you will see no events.

> Full runnable apps (one per framework, each builds in CI): [vskstudio/takt-examples](https://github.com/vskstudio/takt-examples).

## Core (any / no framework)

```bash
pnpm add @vskstudio/takt-core
```

> Runnable: [`examples/core-usage.ts`](./examples/core-usage.ts) · typed events: [`examples/typed-events.ts`](./examples/typed-events.ts)

```ts
import { init, track } from '@vskstudio/takt-core'

// init() creates ONE shared instance, fires an initial pageview, and wires SPA nav.
init({ domain: 'example.com', outbound: true, files: true, excludeLocalhost: false })

track('Signup', {
  props: { plan: 'pro' },                       // values coerced to strings
  revenue: { amount: '29.00', currency: 'EUR' } // amount is a STRING; currency 3 letters
})
```

No-build snippet (queues calls made before load):

```html
<script>window.takt = window.takt || function(){(window.takt.q=window.takt.q||[]).push(arguments)}</script>
<script defer src="https://cdn.jsdelivr.net/npm/@vskstudio/takt-core@0.2.2/dist/takt.js" data-domain="example.com"></script>
```

## React

```bash
pnpm add @vskstudio/takt-react @vskstudio/takt-core
```

```tsx
import { Takt, useTakt } from '@vskstudio/takt-react'

export function App() {
  return (
    <Takt domain="example.com" outbound files={['pdf', 'zip']}>
      <Routes />
    </Takt>
  )
}

function SignupButton() {
  const takt = useTakt() // never-throwing no-op before mount / during SSR
  return <button onClick={() => takt.track('Signup', { props: { plan: 'pro' } })}>Sign up</button>
}
```

Declarative click (also `<TaktEvent name="Buy" props={...} revenue={...}>`):

```tsx
import { useTaktEvent } from '@vskstudio/takt-react'
const onBuy = useTaktEvent({ name: 'Buy', revenue: { amount: '9.00', currency: 'EUR' } })
// <button {...onBuy}>Buy</button>
```

Next.js: render `<Takt>` from the App Router root (entry ships `'use client'`).
React-free embed: `import '@vskstudio/takt-react/element'` → `<takt-analytics domain="example.com" outbound files>`.

## Vue 3

```bash
pnpm add @vskstudio/takt-vue @vskstudio/takt-core
```

```vue
<script setup lang="ts">
import { Takt } from '@vskstudio/takt-vue'
</script>

<template>
  <Takt domain="example.com" :outbound="true" :files="['pdf', 'zip']">
    <RouterView />
  </Takt>
</template>
```

```vue
<script setup lang="ts">
import { useTakt } from '@vskstudio/takt-vue'
const takt = useTakt()
</script>
<template>
  <button @click="takt.track('Signup', { props: { plan: 'pro' } })">Subscribe</button>
  <!-- directive: -->
  <button v-takt-event="{ name: 'Purchase', revenue: { amount: '29.00', currency: 'EUR' } }">Buy</button>
</template>
```

Global install (also bootstraps an instance): `app.use(TaktPlugin, { domain: 'example.com', outbound: true })`.
`vTaktEvent` and core fns are also on `@vskstudio/takt-vue/directives`.

## Svelte 5

```bash
pnpm add @vskstudio/takt-svelte @vskstudio/takt-core
```

```svelte
<!-- +layout.svelte -->
<script>
  import { Takt } from '@vskstudio/takt-svelte'
</script>
<Takt domain="example.com" outbound files />
```

```svelte
<script>
  import { useTakt } from '@vskstudio/takt-svelte'
  const takt = useTakt()
</script>
<button onclick={() => takt.track('Signup', { props: { plan: 'pro' } })}>Sign up</button>
```

Action style (drive `init()` yourself), from `@vskstudio/takt-svelte/actions`:

```svelte
<script>
  import { init, taktEvent } from '@vskstudio/takt-svelte/actions'
  init({ domain: 'example.com' })
</script>
<button use:taktEvent={{ name: 'Signup', props: { plan: 'pro' } }}>Sign up</button>
```

Web component: `import '@vskstudio/takt-svelte/element'` → `<takt-analytics domain="example.com" outbound files>`.

## Solid

```bash
pnpm add @vskstudio/takt-solid @vskstudio/takt-core
```

```tsx
import { Takt, useTakt } from '@vskstudio/takt-solid'

export function App() {
  return (
    <Takt domain="example.com" outbound files={['pdf', 'zip']}>
      <Routes />
    </Takt>
  )
}

function SignupButton() {
  const takt = useTakt()
  return <button onClick={() => takt.track('Signup', { props: { plan: 'pro' } })}>Sign up</button>
}
```

Declarative: `createTaktEvent({ name, props, revenue })` → spread `{...onClick}`, or `<TaktEvent name="Signup" props={{ plan: 'pro' }}>`.
Solid-free embed: `import '@vskstudio/takt-solid/element'`.

## Angular 17+

```bash
pnpm add @vskstudio/takt-angular @vskstudio/takt-core
```

```ts
// main.ts
import { bootstrapApplication } from '@angular/platform-browser'
import { provideTakt } from '@vskstudio/takt-angular'
import { AppComponent } from './app/app.component'

bootstrapApplication(AppComponent, {
  providers: [provideTakt({ domain: 'example.com', outbound: true, files: true })],
})
```

```ts
import { Component, inject } from '@angular/core'
import { TaktService, TaktEventDirective } from '@vskstudio/takt-angular'

@Component({
  standalone: true,
  imports: [TaktEventDirective],
  template: `
    <button taktEvent="Signup" [taktProps]="{ plan: 'pro' }"
            [taktRevenue]="{ amount: '29.00', currency: 'EUR' }">Sign up</button>
  `,
})
export class CheckoutComponent {
  private readonly takt = inject(TaktService) // no-op before init / on server
  buy() { this.takt.track('Purchase', { props: { plan: 'pro' } }) }
}
```

Other exports: `TAKT_CONFIG` (InjectionToken), `defineTaktElement` (from `@vskstudio/takt-angular/element`).

## Astro

```bash
pnpm add @vskstudio/takt-astro @vskstudio/takt-core
```

Pick ONE path — both boot core's default instance, so combining them double-boots.

```js
// astro.config.mjs — integration (recommended)
import { defineConfig } from 'astro/config'
import takt from '@vskstudio/takt-astro'

export default defineConfig({
  integrations: [takt({ domain: 'example.com' })],
})
```

```astro
---
// or the component, per-layout, in <head>
import Takt from '@vskstudio/takt-astro/Takt.astro'
---
<head><Takt domain="example.com" /></head>
```

Astro tracks `astro:after-swap` (View Transitions) instead of core's history patch, so it counts each navigation exactly once. Custom events: `import { track } from '@vskstudio/takt-astro'`. The Astro `files` option is boolean only (no extension array).
