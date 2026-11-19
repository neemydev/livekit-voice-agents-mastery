# Progress Log

Newest entry at the top. Each entry: what we did, what we learned, what is next.

---

## 2026-11-19 — Four projects, Docker, GitHub-ready

**Done**
- Decided the four projects: `dental_receptionist`, `restaurant` (multi-agent), `healthcare`, `contact_center`.
- Code goes in `agents/<project>/`, specs in `specs/<project>/NNN-<feature>/`. Inner layout: decided per project later.
- Spec gate now works per project: code is allowed only while that project has an open plan (Approved or Built).
- Added `.env.example` (key names only) so the repo is safe to publish on GitHub.
- All projects will run in Docker (Docker 29 + Compose installed). Docker files come with the first project's plan.

**Learned**
- Python can't import folder names with dashes, so project folders use underscores.
- Wrote the tests for the new gate rule first, watched 7 fail, then changed the hook until all 25 passed.

**Next**
- Add LiveKit Cloud keys to `.env`. First commit.
- `/lesson voice-ai-foundations`, then `/new-spec dental_receptionist ...`.

---

## 2026-11-19 — Adopted Anthropic's AI-native SDLC playbook

**Done**
- Specs are now one folder per agent with 3 files: `intent.md` → `spec.md` → `plan.md`.
- New shortcut `/plan` (plan mode, then build). `/new-spec` now does intent + spec.
- Two hooks: `protect_env` (keeps `.env` away from Claude) and `spec_gate` (no agent code before the plan is Approved).
- First feedback loop: `uv run pytest` runs 24 tests for the hooks. All pass.
- Turned on git.

**Learned**
- A **skill** is advice Claude should follow. A **hook** is a rule the tool enforces every time.
- The tests caught a real mistake: `.env.example.bak` was blocked by accident. Fixed it.
- Each stage writes a small file, so the next stage (or a new chat) can pick up where we left off.

**Next**
- Add LiveKit Cloud keys to `.env`.
- `/lesson voice-ai-foundations`, then `/new-spec` for the first agent.

---

## 2026-11-19 — Project setup

**Done**
- Tested the OpenAI, Deepgram and Speechmatics API keys. All three answered with real results.
- Added the LiveKit docs MCP server (`.mcp.json`), so Claude reads the latest docs.
- Created `CLAUDE.md`, `specs/`, `progress/` and `.claude/commands/`.

**Learned**
- A key can be "valid" but still fail if the account has no credit. A real small request checks both.

**Next**
- Create a LiveKit Cloud project and add `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET` to `.env`.
- Start course: Track 1, "Voice AI Foundations".
- Write spec `001` for our first voice agent.
