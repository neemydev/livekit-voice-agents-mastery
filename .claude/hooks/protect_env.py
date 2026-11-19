#!/usr/bin/env python3
"""Hook: stop Claude from reading, changing or printing .env files.

Why: .env holds the real API keys. Claude never needs to see them.
Code loads them itself (for example with python-dotenv).

Allowed: example files such as .env.example (they hold no real keys).
Blocked: Read/Edit/Write/Grep on .env or .env.<anything>, and any Bash
command that names such a file.

Exit code 2 = block the action. The text on stderr is shown to Claude.
"""
import json
import os
import re
import sys

SAFE_WORDS = {"example", "sample", "template"}

# A ".env" file name, alone or with a suffix: .env, .env.local, .env.production
ENV_IN_TEXT = re.compile(r"(?:^|[\s/'\"=<>(:])(\.env(?:\.[\w.-]+)?)(?=$|[\s'\";|&)<>])")


def is_secret_env_name(name: str) -> bool:
    name = os.path.basename(name)
    if not (name == ".env" or name.startswith(".env.")):
        return False
    return not (SAFE_WORDS & set(name.split(".")))


def block(reason: str) -> None:
    print(reason, file=sys.stderr)
    sys.exit(2)


def main() -> None:
    data = json.load(sys.stdin)
    tool = data.get("tool_name", "")
    tool_input = data.get("tool_input", {}) or {}

    if tool in ("Read", "Edit", "Write", "MultiEdit", "NotebookEdit", "Grep"):
        path = tool_input.get("file_path") or tool_input.get("notebook_path") or tool_input.get("path") or ""
        if is_secret_env_name(path):
            block(
                f"Blocked by project hook (protect_env): '{os.path.basename(path)}' holds secret keys. "
                "Claude must not read or change it. Ask the user to edit it, or use .env.example for key names."
            )

    if tool == "Bash":
        command = tool_input.get("command", "")
        for match in ENV_IN_TEXT.finditer(command):
            if is_secret_env_name(match.group(1)):
                block(
                    "Blocked by project hook (protect_env): this command touches a .env file, "
                    "which holds secret keys. Let the program load .env itself (python-dotenv), "
                    "or ask the user to run the command."
                )

    sys.exit(0)


if __name__ == "__main__":
    main()
