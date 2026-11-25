# LiveKit Voice Agent — Learning Project

This project is for **learning how to build LiveKit voice agents**.
The user is the learner and learns by doing. Claude is the instructor: explain each idea simply
before using it, explain the code you write, and suggest small "try it yourself" tasks.

## The four projects

Each project has its own folder in `agents/` (inner layout to be decided per project) and its own specs in `specs/`.
All of them run in **Docker**. The repo will be published on GitHub, so keep it clean and secret-free.

| Project | Code | Specs | Main course |
|---|---|---|---|
| Dental receptionist | `agents/dental_receptionist/` | `specs/dental_receptionist/` | Voice AI Foundations |
| Restaurant (multi-agent) | `agents/restaurant/` | `specs/restaurant/` | Tools, Tasks & Workflows |
| Healthcare agent | `agents/healthcare/` | `specs/healthcare/` | to decide |
| Contact center | `agents/contact_center/` | `specs/contact_center/` | AI-Powered Contact Centers |

## How we work (from Anthropic's AI-native SDLC playbook)

Every piece of work goes through these steps. Each step writes a file. The user approves each one.

1. **Intent** → `specs/<project>/NNN-<feature>/intent.md` (what and why, in the user's words) — `/new-spec`
2. **Spec** → `spec.md` in the same folder (how it must behave)
3. **Plan** → `plan.md`, made in **plan mode** (read-only) — `/plan`
4. **Build** → `agents/<project>/` — only while the project has an open plan (Approved or Built)
5. **Test** → run the tests, paste the output into plan.md
6. **Log** → `/log-progress`

Set a status to `Approved` only after the user says yes in the chat. Details: `specs/README.md`.

## Rules

- **LiveKit docs, not memory.** Use the `livekit-docs` MCP server and the `livekit-agents` skill before writing LiveKit code. Check Docker setup against the docs too.
- **Proof before "done".** Run the tests and show the output. A bug fix starts with a failing test.
- **Git: the user commits, not Claude.** Never run `git commit` or `git push`. At the end of a piece of work, give the user a ready-to-copy commit message. Never add `Co-Authored-By` or any Claude/AI attribution.
- **Branches: one per feature, no `develop`.** ⏸ **PAUSED** (user, 2026-11-25): work on `main` and skip
  the branch checks until the user says to start using branches. When on: each spec gets a branch named like its folder,
  e.g. `dental_receptionist/002-clinic-facts`, made from the latest `main`. Never build on `main`.
  Finished work goes to `main` through a Pull Request that the user merges. Steps: `specs/README.md`.
- **Secrets.** Never read, print or change `.env`. Code loads it with python-dotenv. New key names go in `.env.example` (empty values).

## Glossary

`GLOSSARY.md` — one file, grouped by topic, A-Z inside each group. Each entry: 2-3 simple lines.
Add terms the user asks for. When a new key term comes up, **suggest** adding it (don't add without asking).

## Commands

- Tests (all): `uv run pytest` · one project: `uv run pytest agents/<project>`
- uv workspace: each agent is a package listed in the root `pyproject.toml` (`[tool.uv.workspace] members`). Add a package to one agent: `uv add --package <name> <package>` · root dev tools: `uv add --dev <package>`
- Stack (LiveKit server + agents, local mode): `docker compose up -d` · `docker compose ps` (livekit healthy) · `docker compose logs -f <service>` · `docker compose down` · after code changes: `docker compose up -d --build <service>`
- Cloud mode (same agents, LiveKit Cloud): `docker compose -f docker-compose.yml -f docker-compose.cloud.yml up -d <service>`
- Talk to an agent on the local server: `lk token create --url ws://localhost:7880 --api-key devkey --api-secret secret --join --room <new-room> --identity patient --agent <agent_name> --open meet` (new room name each time). `lk` defaults to the Cloud project.
- Console mode (terminal, no server, use headphones): `uv run python -m dental_receptionist.agent console`
- Watch a call (only the `[call]` lines; Docker logs are JSON): `docker compose logs -f --no-log-prefix dental_receptionist | jq -R -r 'fromjson? | select((.message // "") | startswith("[call]")) | .message'`
- Tests that need the server, the agent container, or an API key are skipped (not failed) when it is missing.

## Hooks (always on, in `.claude/settings.json`)

- `protect_env.py` — blocks any tool or command that touches `.env`.
- `spec_gate.py` — blocks code in `agents/<project>/` unless `specs/<project>/*/plan.md` is Approved or Built.
- Their tests: `tests/test_hooks.py`.

## Courses

- LiveKit Academy: https://www.livekit-academy.com/courses (main course) — `/lesson <slug>`
- Anthropic AI-native SDLC playbook: https://academy.claude.com/courses/ai-native-sdlc-playbook

## Setup facts

- Python 3.13 with `uv`. Docker 29 + Compose installed. Git repo on branch `main`.
- **GitHub: PERSONAL account only, never the work one.**
  - Repo: https://github.com/neemydev/livekit-voice-agents-mastery (public)
  - Remote: `git@github-personal:neemydev/livekit-voice-agents-mastery.git` (the `github-personal` SSH alias uses the personal key)
  - Commit identity (set locally in this repo): `neemydev <neemydev@gmail.com>`. The global git identity is the work one, so never remove the local setting.
- `.env` has OpenAI, Deepgram and Speechmatics keys (all tested OK on 2026-11-19).
- `.env` also has `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET` for LiveKit Cloud project "Learning" (tested OK on 2026-11-22). `lk cloud auth` is done on this Mac.

## Lessons learned (add a line each time Claude repeats a mistake)

- Bash commands whose text contains a `.env` path (even inside a heredoc) are blocked. Write such files with the Write tool.
- Claude cannot set a `plan.md` to `Approved` (it opens the code gate; the safety check blocks it). Save the plan as `Draft` and ask the user to change the Status line.
- Deepgram's default USA server is slow and unsteady from this network (choppy voice). Use the EU server (`api.eu.deepgram.com`); prove it with the voice speed test.
- Never run `docker compose config` without `--quiet`: it prints the keys from `.env`.
