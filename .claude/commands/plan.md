---
description: Make the build plan in plan mode (stage 3), then build after approval
argument-hint: <project>/<NNN-feature>
---

Work item: $ARGUMENTS  (folder: `specs/$ARGUMENTS/`)

1. Check that `intent.md` and `spec.md` in that folder both say `Approved`. If not, stop and tell the user.
2. Enter plan mode (read-only). Read the spec, the existing code in `agents/<project>/`, and the LiveKit docs (livekit-docs MCP).
3. Propose the plan using the sections of `specs/_templates/plan.md`: files that change, order of work, risks, proof.
   Every plan must include tests and the exact test command. Include Docker files if the project needs them.
4. Explain the plan simply, so the user can question it. Wait for approval.
5. After the user approves: write `specs/$ARGUMENTS/plan.md` with Status `Approved`. The spec_gate hook now lets code into `agents/<project>/`.
6. Build it, step by step, explaining each part like an instructor.
7. Run the tests. Paste the real output into plan.md under "After building". Set Status to `Built`.
   Set it to `Tested` only after the user has tried it and is happy. That closes the plan.
8. Never say "done" without showing passing test output.
