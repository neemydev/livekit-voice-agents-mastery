# Progress Log

Newest entry at the top. Each entry: what we did, what we learned, what is next.

---

## 2026-11-23 — First voice agent: dental receptionist 001

**Done**
- Lessons: Voice AI Foundations chapters 1 (what is voice AI) and 2 (project setup).
- Wrote intent, spec and plan for `specs/dental_receptionist/001-first-agent/`. The plan is now **Tested**.
- Built the agent: Deepgram ears and mouth, OpenAI brain (`gpt-5.4-mini`), local turn detector.
- It greets callers as Bright Smile Dental. It doesn't make up hours or bookings.
- Runs in Docker next to my own LiveKit server. One extra compose file switches it to LiveKit Cloud.
- Talked to it 3 ways: console (terminal), local server (Meet page), LiveKit Cloud.
- Tests: 5 new (3 behavior, 1 voice speed, 1 joins a room). Full run: 33 passed.
- Added about 40 glossary terms, and a new Docker group.

**Learned**
- Each call is a "job" that runs in its own process. `async`/`await` lets one call listen while it waits for the LLM.
- Choppy voice was the network, not the code: Deepgram's USA server was too slow from here. The EU server fixed it.
- A speed test proves the fix. Using the median of 3 tries stops one unlucky try from failing it.
- Each container has its own `127.0.0.1`. The agent shares livekit's network, so the audio address works.
- Multi-stage build + `.dockerignore`: a smaller image, with no `.env` inside.
- An LLM judge test fails when the intent is unclear. Make the intent clearer; don't make the check weaker.
- Use headphones in console mode, or the agent hears itself and answers itself.

**Next**
- `/lesson voice-ai-foundations` chapter 3: Understanding AgentSession.
- Then spec 002: give the receptionist real clinic facts (hours, prices).
- Later: Postgres + pgvector in the same compose file, when the agent needs a database.

---

## 2026-11-20 — Self-hosted LiveKit server running in Docker

**Done**
- Wrote and approved intent, spec and plan for `specs/infra/001-local-livekit-server/`. The plan is now **Tested**.
- `docker compose up -d` starts LiveKit `v1.13.11` locally. Settings in `infra/livekit/livekit.yaml`, every line commented.
- Ports: 7880 signaling/API, 7882 UDP media (main), 7881 TCP media (backup). Mapped to `127.0.0.1` only.
- 3 new tests (server says OK, create/list/delete a room, wrong secret refused). With the server off they skip.
- Real media test: the demo bot streamed video, and I saw it in my browser through my own server.
- Added 24 glossary terms (SFU, P2P, MCU, signaling, ICE, UDP mux, bind address, health check, ...).

**Learned**
- An SFU gets each track **once** and forwards copies. No mixing, so it's fast. P2P and MCU don't scale as well.
- Signaling (setup talk, WebSocket 7880) and media (the sound itself, UDP 7882) take different roads.
- In a container, the server must listen on `0.0.0.0`, and it must tell browsers to send media to `127.0.0.1`.
- The server log shows which road won: `[selected] udp4 127.0.0.1:7882`. That is ICE at work.
- A container can say "healthy" while media still fails. Only a real media test proves it.

**Next**
- Start a new chat, so the `livekit-docs` MCP server loads.
- Spec 002: our first voice agent, connected to the local server. Decide: agent on the Mac first, or in Docker?

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
