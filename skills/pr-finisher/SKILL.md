---
name: pr-finisher
description: Use when finalizing a pull request after implementing a plan — runs a fixed finishing checklist with inline checks: real verification (tests/lint/build with evidence), diff hygiene, code quality + project-architecture conformance, security, breaking changes & migrations, perf & accessibility, docs/CHANGELOG, and the PR message. Invoked manually by the user before merge.
---

# PR Finisher

## Overview

Run this manually at PR time, once a plan is implemented and you're about to merge. It does its **own inline checks** here — it does **not** delegate to `/code-review` or `/security-review` (those exist as deeper, complementary tools; see the closing note). The governing rule is **evidence before claims**: never say a check passed without running the command and showing its real output. No "should pass", no "tests probably green" — run it, paste it, then conclude. Web search is allowed and encouraged to validate a judgment call against the language/framework's current best practices.

## Checklist

Create one TodoWrite item per step below and execute them **in order**, marking each complete only after its evidence is in hand.

1. **Verification.** Actually run the project's test, lint, and build commands and paste the real terminal output. Do not summarize from memory or assert "should pass". If you don't know the commands, discover them: read `package.json` scripts, `Makefile`, `Cargo.toml`/`go.mod`, or the CI config (`.github/workflows/*`, `.gitlab-ci.yml`) and run exactly what CI runs. If a check fails: fix trivial failures (lint, formatting, an obvious typo) and re-run. For anything non-trivial — a genuine test failure, an unclear build error — STOP and report it to the user instead of silently debugging; finishing a PR is not the time to disappear into a rabbit hole. A red checklist item blocks the PR until resolved or explicitly waived by the user.

2. **Diff hygiene.** Review `git diff` (and `git diff --staged`) line by line for: leftover debug output (`console.log`, `debugger`, `dbg!`, `println!`, stray `fmt.Println`), `TODO`/`FIXME` left unaddressed, hardcoded secrets/API keys/tokens, commented-out dead code, and stray/parasitic files (build artifacts, `dist/`, `.env`, `*.log`, editor/OS files like `.DS_Store`, `.idea/`). Remove anything that shouldn't ship; confirm `git status` is clean of junk.

3. **Quality + architecture conformance.** Read the project's own conventions — `CLAUDE.md`/`AGENTS.md`, the folder structure, and sibling files near your changes — then verify the diff **respects them**: layering, naming conventions, module boundaries, and where each new file belongs. Check for reuse (no duplicated logic that already exists), simplification opportunities, and appropriate altitude (no over-engineering, no leaky abstractions). When a call is non-obvious, web-search the language/framework's current best practice rather than guessing.

4. **Security.** Inline-review the diff for: unvalidated or untrusted input reaching sensitive sinks, injection risks (SQL, command, XSS, path traversal), hardcoded secrets, authz/authn gaps (missing permission checks, broken access control), and risky new dependencies (unmaintained, typosquatted, or over-permissioned). Flag each finding with the file and line.

5. **Breaking changes & migrations.** Detect and explicitly call out: changed public API signatures or exports, removed/renamed symbols, DB schema migrations, config/env-var additions or changes, and any required deploy or rollback steps. If a consumer must change to adopt this, that is a breaking change — say so loudly; it must land in the PR message.

6. **Perf & accessibility.** Targeted to what the diff actually touches: N+1 queries, allocations or I/O inside hot loops, unbounded collection/cache growth, and missing pagination. If the diff changes UI, also check accessibility — form labels, image alt text, keyboard navigation, focus order, and color contrast. Skip the a11y portion only when no UI changed.

7. **Docs / CHANGELOG.** If public behavior changed, update the docs to match: README, public doc comments / docstrings, and the CHANGELOG. If nothing user-facing changed, state that explicitly so it's a deliberate decision, not an oversight.

8. **PR message.** Write a title plus a **what / why** description, and link to the plan or spec this implements. Summarize the notable risks surfaced in steps 4–6 (security findings, breaking changes, migrations, perf caveats) so reviewers see them up front.

9. **Final summary.** Present the completed checklist with the evidence captured per item (command output, diff notes, decisions). **Only then** offer to push the branch and open the PR — never push before the summary is on the table.

## Red flags — STOP and correct

| Rationalization | What to do instead |
|---|---|
| "Tests probably pass." | Run them and paste the output. Evidence, not optimism. |
| "Small diff, skip the review." | Still scan every changed line — small diffs hide secrets and N+1s too. |
| "It matches my style." | Check the **project's** conventions (`CLAUDE.md`, siblings), not yours. |
| "I'll note the breaking change later." | Call it out now, in the PR message — "later" never comes. |
| "Lint warnings are fine." | CI's gate is the bar — run the linter, then fix each warning or get the user to waive it explicitly. |
| "No tests needed for this." | Name the behavior this change adds and where it's tested; if nothing covers it, say so to the user out loud. |

## Closing note

These are inline checks by design. For deeper, complementary passes, `/code-review` (correctness + reuse/simplification) and `/security-review` (full security audit) exist as separate tools — mention them to the user if a finding warrants a heavier review. The evidence-before-claims discipline here mirrors the superpowers `verification-before-completion` skill.
