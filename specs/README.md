# Specs

Every piece of work gets a spec folder here, written **before** any code.
This follows Anthropic's "AI-native SDLC playbook": each stage writes a small
file, the next stage reads it, and a human approves at each step.

## Grouped by project

Each of the four projects has its own folder. Inside, one numbered folder per feature:

```text
specs/
  dental_receptionist/
    001-first-call/
      intent.md   Stage 1 - what and why, in your own words
      spec.md     Stage 2 - how it must behave
      plan.md     Stage 3 - which files, what order, how we prove it works
  restaurant/
    001-greeter/
    002-order-taking/
```

The project name matches the code folder: `specs/restaurant/` goes with `agents/restaurant/`.
Small fixes may use a folder with only `plan.md`.

## The steps and the gates

| Step | File | Who writes | Gate (who says yes) |
|---|---|---|---|
| 1. Plan | intent.md | Claude asks questions, drafts | You approve |
| 2. Design | spec.md | Claude, using the LiveKit docs | You approve |
| 3. Build plan | plan.md | Claude, in plan mode (read-only) | You approve |
| 4. Build | agents/PROJECT/ | Claude | The hook checks for an open plan |
| 5. Test | test output in plan.md | Claude runs the tests | You check the proof |

Templates are in `_templates/`. Shortcuts: `/new-spec` (steps 1-2), `/plan` (step 3 onwards).

## Branches

Each feature gets its own git branch, named like its spec folder. No `develop` branch.
`main` always holds finished, working code.

```bash
# Start (before /new-spec writes anything)
git switch main
git pull
git switch -c dental_receptionist/002-clinic-facts

# Work: intent → spec → plan → build → test. Commit on this branch.

# Finish (after plan.md is Tested)
git push -u origin dental_receptionist/002-clinic-facts
#   → on GitHub: open a Pull Request, read the changes, click "Merge"
git switch main
git pull
git branch -d dental_receptionist/002-clinic-facts
```

You make the commits, push, and merge. Claude reminds you of these steps.

## Status words

- intent.md and spec.md: `Draft` → `Approved`
- plan.md: `Draft` → `Approved` → `Built` → `Tested`

A plan is **open** while it is `Approved` or `Built`. The hook only lets code into
`agents/PROJECT/` while that project has an open plan. `Tested` closes it.

Claude may change intent.md and spec.md to `Approved` only after you say yes in the chat.
For **plan.md, you change the Status to `Approved` yourself**: that status opens the code gate,
so a human turns the key (Claude's safety check blocks Claude from doing it).
