"""Tests for the two project hooks in .claude/hooks/.

Each test sends the hook the same JSON that Claude Code sends,
then checks the exit code: 0 = allowed, 2 = blocked.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

HOOKS = Path(__file__).resolve().parent.parent / ".claude" / "hooks"


def run_hook(name, tool_name, tool_input, project_dir=None):
    env = {"CLAUDE_PROJECT_DIR": str(project_dir)} if project_dir else {}
    payload = {"tool_name": tool_name, "tool_input": tool_input, "cwd": str(project_dir or ".")}
    result = subprocess.run(
        [sys.executable, str(HOOKS / name)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env=env,
    )
    return result.returncode, result.stderr


# ---------- protect_env.py ----------

@pytest.mark.parametrize("tool,tool_input", [
    ("Read", {"file_path": "/proj/.env"}),
    ("Read", {"file_path": "/proj/.env.local"}),
    ("Edit", {"file_path": "/proj/.env", "old_string": "a", "new_string": "b"}),
    ("Write", {"file_path": "/proj/agents/restaurant/.env", "content": "KEY=1"}),
    ("Grep", {"pattern": "KEY", "path": "/proj/.env"}),
    ("Bash", {"command": "cat .env"}),
    ("Bash", {"command": "source .env && echo $OPENAI_API_KEY"}),
    ("Bash", {"command": "grep KEY /proj/.env.local | head"}),
    ("Bash", {"command": "git add .env"}),
])
def test_protect_env_blocks_secret_files(tool, tool_input):
    code, err = run_hook("protect_env.py", tool, tool_input)
    assert code == 2
    assert "protect_env" in err


@pytest.mark.parametrize("tool,tool_input", [
    ("Read", {"file_path": "/proj/.env.example"}),
    ("Read", {"file_path": "/proj/.venv/bin/activate"}),
    ("Read", {"file_path": "/proj/CLAUDE.md"}),
    ("Write", {"file_path": "/proj/.gitignore", "content": ".env\n"}),
    ("Bash", {"command": "cp .env.example .env.example.bak"}),
    ("Bash", {"command": "uv run pytest"}),
    ("Bash", {"command": "ls .venv"}),
])
def test_protect_env_allows_normal_files(tool, tool_input):
    code, _ = run_hook("protect_env.py", tool, tool_input)
    assert code == 0


# ---------- spec_gate.py ----------
# Rule: code in agents/<project>/ needs an OPEN plan in specs/<project>/<NNN-feature>/plan.md
# "Open" means status Approved or Built. Tested = finished, so new work needs a new plan.

def make_plan(project, rel_folder, status):
    spec_dir = project / "specs" / rel_folder
    spec_dir.mkdir(parents=True)
    (spec_dir / "plan.md").write_text(f"# Plan\n\n**Status:** {status}\n")


def write_call(project, rel_path):
    return {"file_path": str(project / rel_path), "content": "print('hi')"}


CODE = "agents/restaurant/agent.py"


def test_gate_blocks_when_no_specs_for_project(tmp_path):
    code, err = run_hook("spec_gate.py", "Write", write_call(tmp_path, CODE), tmp_path)
    assert code == 2
    assert "no specs" in err


def test_gate_blocks_when_no_plan_yet(tmp_path):
    (tmp_path / "specs" / "restaurant" / "001-greeter").mkdir(parents=True)
    code, err = run_hook("spec_gate.py", "Write", write_call(tmp_path, CODE), tmp_path)
    assert code == 2
    assert "no open plan" in err


@pytest.mark.parametrize("status", ["Draft", "Tested"])
def test_gate_blocks_when_no_open_plan(tmp_path, status):
    make_plan(tmp_path, "restaurant/001-greeter", status)
    code, err = run_hook("spec_gate.py", "Edit", write_call(tmp_path, CODE), tmp_path)
    assert code == 2
    assert "no open plan" in err


@pytest.mark.parametrize("status", ["Approved", "Built"])
def test_gate_allows_open_plan(tmp_path, status):
    make_plan(tmp_path, "restaurant/001-greeter", status)
    code, _ = run_hook("spec_gate.py", "Write", write_call(tmp_path, CODE), tmp_path)
    assert code == 0


def test_gate_allows_when_any_plan_is_open(tmp_path):
    make_plan(tmp_path, "restaurant/001-greeter", "Tested")
    make_plan(tmp_path, "restaurant/002-order-taking", "Approved")
    code, _ = run_hook("spec_gate.py", "Write", write_call(tmp_path, "agents/restaurant/orders/menu.py"), tmp_path)
    assert code == 0


def test_gate_ignores_files_outside_projects(tmp_path):
    for rel in ["specs/restaurant/001-greeter/plan.md", "progress/log.md", "agents/README.md",
                "Dockerfile", "docker-compose.yml", "CLAUDE.md"]:
        code, _ = run_hook("spec_gate.py", "Write", write_call(tmp_path, rel), tmp_path)
        assert code == 0, rel


def test_gate_matches_the_right_project(tmp_path):
    make_plan(tmp_path, "restaurant/001-greeter", "Approved")
    code, _ = run_hook("spec_gate.py", "Write", write_call(tmp_path, "agents/healthcare/agent.py"), tmp_path)
    assert code == 2
