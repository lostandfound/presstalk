# GitHub-first workflow

This document describes how we use GitHub Issues and Pull Requests to plan and deliver work in this repository. It replaces a previous TypeScript-oriented guide and is tailored to this Python CLI project.

## Principle

- Start every change with a GitHub Issue (features, fixes, docs, refactors, design decisions).
- Keep issues small and outcome-oriented. Link related docs and code.

## Issue types and template

- Types: Feature / Bug / Docs / Task / ADR (architecture decision)
- Recommended sections in the issue body:
  - Context / Goal
  - Scope (in / out)
  - Acceptance criteria (Definition of Done)
  - Risks / Impact / Rollback
  - Test notes (how we will verify)

## Labels

- Required (exactly one each):
  - `type/feature` | `type/bug` | `type/doc` | `type/chore`
  - `priority/p0` | `priority/p1` | `priority/p2`
- Optional (pick at most one):
  - One of these: `area/cli` | `area/core` | `area/docs`
  - Or one platform label: `platform/macos` | `platform/windows` | `platform/linux`
- Rules:
  - Max 3 labels per issue (one type + one priority + optional one area)
  - Do not use status labels; track progress in the issue body (and project board if used)
  - Phase/size granularity should be written in the issue body

Notes:
- Platform labels are defined but not required. Use them when an issue is OS-specific.



## Milestones

- Use milestones for grouping issues when planning a short release or theme. Optional.

## Branches, commits, and PRs

- Branch names: short and descriptive (e.g., `feat/global-hotkey`, `fix/capture-timeout`, `docs/windows-usage`). Including the issue number is optional (e.g., `feat/123-global-hotkey`).
- Commits: imperative present, small and scoped. Reference related issues in the body when relevant.
  - Example: `Add Windows paste backend (clip.exe + Ctrl+V)`
- Pull Requests:
  - Link the primary issue in the title or body (e.g., `Fixes #123`).
  - Include a concise summary, a list of changes, and a clear test plan. Add screenshots/log excerpts when UX/logging changes.
  - CI is not configured. Before requesting review, run unit tests locally and verify the CLI simulation works (see Testing below).

Suggested PR body structure:

```
## Summary
- One or two bullets that describe the purpose

## Changes
- Bullet list of noteworthy changes

## Test plan
- Commands you ran and expected/actual results
- Notes about edge cases and platforms (macOS/Windows)

## Notes
- Risks, rollbacks, and follow-ups
```

## Testing checklist (local)

- Run all unit tests (unittest):

```bash
uv run python -m unittest -v
```

- Optionally run a focused file (example):

```bash
uv run python -m unittest tests/test_controller.py -v
```

- Verify the CLI simulation (no audio device required):

```bash
uv run presstalk simulate --chunks hello world --delay-ms 40
```

- For real capture runs (macOS requires microphone + Accessibility permissions):

```bash
uv run presstalk run
```

## Decision records (ADR)

- For significant architectural decisions, create an ADR issue and document the outcome under `docs/` (e.g., `docs/architecture.md` or a new `docs/adr-XXXX.md`). Link the document from the issue and PR.

## Guardrails

- Prefer linking every PR to an Issue that states the goal and acceptance criteria.
- Keep PRs small and focused; large changes should be split or staged.
- Never commit secrets or credentials. Verify logs and screenshots do not leak sensitive info.
- When modifying user-visible behavior or logs, include examples in the PR description.

## Developer commands (reference)

- Create and activate venv:

```bash
uv venv && source .venv/bin/activate
```

- Editable install with dependencies:

```bash
uv pip install -e .
```

- Run tests:

```bash
uv run python -m unittest -v
```

- Run CLI (simulate / local):

```bash
uv run presstalk simulate --chunks hello world --delay-ms 40
uv run presstalk run
```
