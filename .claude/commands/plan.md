---
description: Make the build plan in plan mode (stage 3), then build after approval
argument-hint: <project>/<NNN-feature>
---

Work item: $ARGUMENTS  (folder: `specs/$ARGUMENTS/`)

1. Check that `intent.md` and `spec.md` in that folder both say `Approved`. If not, stop and tell the user.
   Check the branch (`git branch --show-current`). If it is `main`, stop: give the "Start" commands from
   `specs/README.md` (Branches), with the branch named `$ARGUMENTS`.
2. Enter plan mode (read-only). Read the spec, the existing code in `agents/<project>/`, and the LiveKit docs (livekit-docs MCP).
3. Propose the plan using the sections of `specs/_templates/plan.md`: files that change, order of work, risks, proof.
   Every plan must include tests and the exact test command. Include Docker files if the project needs them.
4. Explain the plan simply, so the user can question it. Wait for approval.
5. After the user approves: write `specs/$ARGUMENTS/plan.md` with Status `Draft`, and ask the user to change
   the Status line to `Approved` themselves (Claude's safety check blocks Claude from doing it).
   Once it says `Approved`, the spec_gate hook lets code into `agents/<project>/`.
6. Build it, step by step, explaining each part like an instructor.
7. Run the tests. Paste the real output into plan.md under "After building". Set Status to `Built`.
   Set it to `Tested` only after the user has tried it and is happy. That closes the plan.
8. Never say "done" without showing passing test output.
9. When the plan is `Tested`: give the user a commit message and the "Finish" commands from `specs/README.md`
   (push the branch, open and merge the Pull Request, switch back to `main`).
