---
description: Start new work - write intent.md, then spec.md (stages 1 and 2)
argument-hint: <project> <short idea>
---

The user wants to build: $ARGUMENTS

Projects: `dental_receptionist`, `restaurant`, `healthcare`, `contact_center` (see CLAUDE.md).
If the project is not clear, ask which one.

**Stage 1 - intent.md**
1. Pick the next number inside `specs/<project>/` (001, 002, ...) and a short feature name (lowercase, dashes).
   **Branch check:** run `git branch --show-current`. If it is not `<project>/<NNN>-<feature>`, give the user
   the "Start" commands from `specs/README.md` (Branches) with this name, and wait until they have run them.
2. Ask the user a few simple questions, one at a time, like an analyst: problem, outcome, who uses it, what they want to learn, limits.
3. Copy `specs/_templates/intent.md` to `specs/<project>/<NNN>-<feature>/intent.md` and fill it in with their words. Status: `Draft`.
4. Show it and ask for approval. Only when they say yes, set Status to `Approved`.

**Stage 2 - spec.md**
5. Research: search the `livekit-docs` MCP server, load the `livekit-agents` skill, and check the matching course lesson.
6. Copy `specs/_templates/spec.md` and fill it in. Put doc links under "What the docs say". Flag anything unclear under "Concerns".
7. Explain it simply. Discuss. Set Status to `Approved` only after the user says yes.

Do NOT write any code. The next step is `/plan <project>/<NNN>-<feature>`.
