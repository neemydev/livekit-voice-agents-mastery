# Plan: <short name>

**Status:** Draft  <!-- Draft → Approved → Built → Tested -->
**Date:** YYYY-MM-DD
**Project:** <project>
**Built from:** spec.md (must be Approved first)

> Stage 3 — BUILD PLAN. Made in plan mode. The spec_gate hook blocks code in
> agents/<project>/ unless a plan for that project is Approved or Built.

## Files that change
| File | New or changed | What it does |
|---|---|---|
| agents/<project>/... | new | |
| agents/<project>/tests/... | new | |

## Order of work
1.
2.

## Risks
What could go wrong, and what we do about it.

## Proof (how we know it works)
- Command: `uv run pytest agents/<project>` (or inside Docker, once set up)
- Tests:
  - [ ]
- Manual check: <for example, talk to it in the LiveKit playground>

## After building (filled in at the end)
- Test output:
- What we changed from the plan, and why:
