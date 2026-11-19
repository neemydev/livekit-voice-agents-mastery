#!/usr/bin/env python3
"""Hook: no project code without an approved plan.

Rule: Claude may only create or edit files in  agents/<project>/...
while that project has an OPEN plan:
  specs/<project>/<NNN-feature>/plan.md  with status Approved or Built.

Status meanings for plan.md:
  Draft    - not approved yet          -> blocked
  Approved - user said yes, build it   -> allowed
  Built    - code written, being tried -> allowed
  Tested   - finished                  -> blocked (new work needs a new plan)

Example:
  agents/restaurant/agent.py  is allowed if
  specs/restaurant/002-order-taking/plan.md  says  **Status:** Approved

Files directly inside agents/ (like agents/README.md) are not gated.
Note: this checks Claude's file tools (Edit/Write). It does not watch Bash.

Exit code 2 = block the action. The text on stderr is shown to Claude.
"""
import json
import os
import re
import sys
from pathlib import Path

OPEN_STATUSES = {"approved", "built"}
STATUS_LINE = re.compile(r"^\W*Status\W*([A-Za-z]+)", re.IGNORECASE | re.MULTILINE)


def block(reason: str) -> None:
    print(reason, file=sys.stderr)
    sys.exit(2)


def plan_status(plan: Path) -> str:
    found = STATUS_LINE.search(plan.read_text(encoding="utf-8"))
    return found.group(1).lower() if found else "missing"


def main() -> None:
    data = json.load(sys.stdin)
    if data.get("tool_name") not in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
        sys.exit(0)

    tool_input = data.get("tool_input", {}) or {}
    raw_path = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not raw_path:
        sys.exit(0)

    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd()).resolve()
    path = Path(raw_path)
    if not path.is_absolute():
        path = root / path
    path = path.resolve()

    try:
        parts = path.relative_to(root).parts
    except ValueError:
        sys.exit(0)  # outside this repo: not our business

    if len(parts) < 3 or parts[0] != "agents":
        sys.exit(0)  # not inside agents/<project>/

    project = parts[1]
    spec_dir = root / "specs" / project
    if not spec_dir.is_dir():
        block(
            f"Blocked by project hook (spec_gate): no specs for project '{project}'. "
            f"Create specs/{project}/001-<feature>/ with intent.md, spec.md and plan.md first (/new-spec)."
        )

    plans = {p.parent.name: plan_status(p) for p in sorted(spec_dir.glob("*/plan.md"))}
    if not any(status in OPEN_STATUSES for status in plans.values()):
        found = ", ".join(f"{name}={status}" for name, status in plans.items()) or "none"
        block(
            f"Blocked by project hook (spec_gate): project '{project}' has no open plan "
            f"(plans found: {found}). Code needs a plan.md with status Approved or Built, "
            "and only the user can approve a plan (/plan)."
        )

    sys.exit(0)


if __name__ == "__main__":
    main()
