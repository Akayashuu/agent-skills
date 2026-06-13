---
name: pr-finisher
description: Use when finalizing a pull request after implementing a plan — runs a fixed finishing checklist: real verification (tests/lint/build with evidence), diff hygiene, then an orchestrated deep security + code-quality/architecture review whose every finding is double-verified by two independent fresh agents (Confirmed/Uncertain/Refuted) to filter false positives, plus breaking changes & migrations, perf & accessibility, docs/CHANGELOG, and the PR message. Invoked manually before merge.
---

# PR Finisher

## Overview

Run this manually at PR time, once a plan is implemented and you're about to merge. It **orchestrates a deep review** — it runs a real security and code-quality/architecture pass (invoke `/code-review` and `/security-review`, and/or dispatch a reviewer subagent per dimension) rather than eyeballing the diff. Two rules govern it:

- **Evidence before claims.** Never say a check passed without running the command and showing its real output. No "should pass" — run it, paste it, then conclude.
- **A finding is not a conclusion until two independent verifiers agree on it.** Reviews surface *candidate* findings; many are plausible-but-false ("false positives"). Each candidate is adversarially double-checked (step 4) before it is allowed into the summary.

Web search is allowed and encouraged to validate a judgment call against the language/framework's current best practices.

## Checklist

Create one TodoWrite item per step below and execute them **in order**, marking each complete only after its evidence is in hand.

1. **Verification.** Actually run the project's test, lint, and build commands and paste the real terminal output. Do not summarize from memory or assert "should pass". If you don't know the commands, discover them: read `package.json` scripts, `Makefile`, `Cargo.toml`/`go.mod`, or the CI config (`.github/workflows/*`, `.gitlab-ci.yml`) and run exactly what CI runs. If a check fails: fix trivial failures (lint, formatting, an obvious typo) and re-run. For anything non-trivial — a genuine test failure, an unclear build error — STOP and report it to the user instead of silently debugging; finishing a PR is not the time to disappear into a rabbit hole. A red checklist item blocks the PR until resolved or explicitly waived by the user.

2. **Diff hygiene.** Review `git diff` (and `git diff --staged`) line by line for: leftover debug output (`console.log`, `debugger`, `dbg!`, `println!`, stray `fmt.Println`), `TODO`/`FIXME` left unaddressed, hardcoded secrets/API keys/tokens, commented-out dead code, and stray/parasitic files (build artifacts, `dist/`, `.env`, `*.log`, editor/OS files like `.DS_Store`, `.idea/`). Remove anything that shouldn't ship; confirm `git status` is clean of junk.

3. **Review — collect candidate findings.** Run a thorough review and gather *candidates* (not conclusions) across these dimensions. Orchestrate it: invoke `/code-review` (correctness + reuse/simplification) and `/security-review` (security audit), and/or dispatch a dedicated reviewer subagent per dimension. Normalize every candidate to `dimension · claim · file:line · why`.
   - **Quality + architecture conformance.** Read the project's conventions — `CLAUDE.md`/`AGENTS.md`, folder structure, sibling files near your changes — and flag where the diff violates them: layering, naming, module boundaries, file placement. Plus duplicated logic that already exists, simplification opportunities, and over-engineering / leaky abstractions.
   - **Security.** Unvalidated/untrusted input reaching sensitive sinks, injection (SQL, command, XSS, path traversal), hardcoded secrets, authz/authn gaps (missing permission checks, broken access control), and risky new dependencies (unmaintained, typosquatted, over-permissioned).
   - **Breaking changes & migrations.** Changed public API signatures or exports, removed/renamed symbols, DB schema migrations, config/env-var changes, and required deploy/rollback steps.
   - **Perf & accessibility.** N+1 queries, allocations or I/O in hot loops, unbounded collection/cache growth, missing pagination. If the diff changes UI: form labels, image alt text, keyboard navigation, focus order, color contrast. Skip the a11y portion only when no UI changed.

4. **Adversarial double-verification.** This is the false-positive filter. For **each** candidate finding from step 3, dispatch **two** fresh, independent verifier subagents **in parallel**. Give each verifier *only*: the finding (`claim + file:line + why`) and repo access — not the other findings, not your reasoning. Instruct each: *"This finding may be a false positive. Read the actual code and try to REFUTE it."* Each verifier returns one verdict:
   - **Confirmed** — with proof: `file:line` + an exploitation scenario (security) / reproduction (bug, perf) / the exact duplicated blocks (quality).
   - **Uncertain** — can neither confirm nor refute; states what's missing.
   - **Refuted** — with a one-line reason (e.g. "sink not reachable", "the two blocks differ on the permission check, so not DRY").

   **Agreement rule (2 votes):**
   - both **Confirmed** → **Confirmed**
   - both **Refuted** → **Refuted**
   - anything else (disagreement, or at least one **Uncertain**) → **Uncertain** (human judgment required).

   *Fallback:* if the runtime cannot dispatch subagents, run two **separate** inline adversarial passes over each finding (each a clean refutation attempt) and apply the same agreement rule. Independent subagents are the default; inline is graceful degradation.

5. **Docs / CHANGELOG.** If public behavior changed, update the docs to match: README, public doc comments / docstrings, and the CHANGELOG. If nothing user-facing changed, state that explicitly so it's a deliberate decision, not an oversight.

6. **PR message.** Write a title plus a **what / why** description, and link to the plan or spec this implements. Surface the **Confirmed + Uncertain** risks (security, breaking changes, migrations, perf) so reviewers see them up front. Refuted findings do **not** go in the PR message.

7. **Final summary.** Present:
   - the **Confirmed** findings (each with its proof) and the **Uncertain** findings (clearly marked "human judgment required"),
   - a **"Refuted (dropped)"** section listing each false positive in one line with its reason — nothing is hidden,
   - the evidence captured in steps 1–2 (command output, diff notes).

   **Only then** offer to push the branch and open the PR — never push before the summary is on the table.

## Red flags — STOP and correct

| Rationalization | What to do instead |
|---|---|
| "Tests probably pass." | Run them and paste the output. Evidence, not optimism. |
| "Small diff, skip the review." | Still scan every changed line — small diffs hide secrets and N+1s too. |
| "It matches my style." | Check the **project's** conventions (`CLAUDE.md`, siblings), not yours. |
| "I'll note the breaking change later." | Call it out now, in the PR message — "later" never comes. |
| "Lint warnings are fine." | CI's gate is the bar — run the linter, then fix each warning or get the user to waive it explicitly. |
| "No tests needed for this." | Name the behavior this change adds and where it's tested; if nothing covers it, say so to the user out loud. |
| "This finding is obviously real — skip verification." | Refute it anyway: two fresh verifiers, refutation posture. Obviousness is proven, not assumed. |

## Closing note

The deep review is orchestrated here on purpose: `/code-review` (correctness + reuse/simplification) and `/security-review` (full security audit) are the heavier passes this skill drives, and their findings are only as trustworthy as the double-verification in step 4. The evidence-before-claims discipline mirrors the superpowers `verification-before-completion` skill.
