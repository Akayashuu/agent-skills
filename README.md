# agent-skills

A collection of **framework/language expert skills** for [Claude Code](https://docs.claude.com/en/docs/claude-code) (and any agent runtime following the [Agent Skills](https://agentskills.io/specification) spec).

Each skill is a concise, scannable reference of *idiomatic, modern best practices* — the judgment calls a linter can't make. They load on demand when a task matches their `description`.

## Skills

| Skill | Use when |
|-------|----------|
| [`typescript-expert`](skills/typescript-expert/SKILL.md) | Writing/reviewing TypeScript — modelling data, generics, fixing `any`/enum/unsound casts |
| [`react-expert`](skills/react-expert/SKILL.md) | Writing React — re-renders, state vs derived, `useEffect` overuse, keys, server components |
| [`vue-expert`](skills/vue-expert/SKILL.md) | Writing Vue 3 — Composition API, `ref`/`reactive`, `computed` vs `watch`, `script setup` |
| [`svelte-expert`](skills/svelte-expert/SKILL.md) | Writing Svelte 5 — runes (`$state`/`$derived`/`$effect`), migrating legacy `$:`/`export let` |
| [`solid-expert`](skills/solid-expert/SKILL.md) | Writing SolidJS — signals, fine-grained reactivity, props (don't destructure!), stores |
| [`angular-expert`](skills/angular-expert/SKILL.md) | Writing Angular — standalone components, signals, `inject()`, new control flow, RxJS teardown |
| [`astro-expert`](skills/astro-expert/SKILL.md) | Building Astro — islands, client directives, content collections, View Transitions |
| [`php-expert`](skills/php-expert/SKILL.md) | Writing/reviewing PHP 8.1+ — enums & readonly value objects, `match` over `switch`, exceptions vs result types, PSR interfaces & Composer autoloading, PHPStan types |
| [`laravel-expert`](skills/laravel-expert/SKILL.md) | Building Laravel apps/packages — service providers, container bindings, Eloquent/N+1, form requests, queued jobs, events, facades vs DI, Testbench/Pest |
| [`symfony-expert`](skills/symfony-expert/SKILL.md) | Building Symfony 6.4/7.x apps/bundles — DI container (autowiring, tags, `#[Autowire]`, compiler passes), bundle Extension/Configuration, attribute routing, Twig, HttpClient, Flex |
| [`takt-expert`](skills/takt-expert/SKILL.md) | Integrating [Takt](https://www.npmjs.com/package/@vskstudio/takt-core) analytics or authoring a `@vskstudio/takt-*` wrapper |
| [`go-expert`](skills/go-expert/SKILL.md) | Writing Go — error wrapping (`errors.Is/As`, `%w`), goroutine/context cancellation & leaks, consumer-side interfaces, useful zero values, generics restraint |
| [`rust-expert`](skills/rust-expert/SKILL.md) | Writing Rust — ownership vs reflexive `clone()`, `Result`/`?` & thiserror/anyhow, avoiding `unwrap()`, generics vs `dyn`, isolating `unsafe` |
| [`pr-finisher`](skills/pr-finisher/SKILL.md) | Finalizing a PR — verification, diff hygiene, quality + architecture conformance, security, breaking changes/migrations, perf/a11y, docs, PR message |

## Install as a Claude Code plugin

Add this repo as a plugin marketplace, then install the plugin to get all 14 skills at once:

```
/plugin marketplace add Akayashuu/agent-skills
/plugin install agent-skills@agent-skills
```

Skills are discovered automatically and load on demand when a task matches their `description`. Update later with `/plugin marketplace update agent-skills`.

## Install manually

Copy the skills you want into your agent's skills directory:

```bash
# Claude Code (personal, all projects)
cp -r skills/* ~/.claude/skills/

# or per-project (committed with the repo)
cp -r skills/* .claude/skills/
```

Then ask Claude Code as usual — it loads the relevant skill when your task matches.

## License

MIT
