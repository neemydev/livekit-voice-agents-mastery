# Plan: dental_receptionist 001 — first agent (greet and chat)

**Status:** Built  <!-- Draft → Approved → Built → Tested --> (built 2026-11-22; approved by user 2026-11-22)
**Date:** 2026-11-22
**Project:** dental_receptionist
**Built from:** spec.md (Approved 2026-11-22)

> Stage 3 — BUILD PLAN. Made in plan mode. The spec_gate hook blocks code in
> agents/<project></project>/ unless a plan for that project is Approved or Built.

## Context

You understand the chapter 2 code, but you have no agent of your own yet. The intent and spec
(both Approved) say: a Bright Smile Dental receptionist that says hello first and chats in short
replies. It runs in Docker next to **your own LiveKit server** by default, can switch to LiveKit
Cloud by settings only, and uses Deepgram (ears and mouth) and OpenAI (brain) with your own keys.
It doesn't make up facts or bookings.

## Decisions made in this plan (the open points from the spec)

1. **OpenAI model: `gpt-5.4-mini`, with a low reasoning (thinking) setting.** Your key can use it
   (I checked the model list). It's current and not being retired. A low thinking setting keeps
   replies fast. If it feels slow in the voice test, we switch to `gpt-4.1-mini`, which is also on your key.
2. **Python layout: a uv "workspace".** The root `pyproject.toml` becomes the workspace (one
   project made of several small packages), and each agent is one package inside it. One
   `uv.lock` for the whole repo. `uv run pytest` from the root still runs every test. The Docker
   image installs **only** this agent's packages (`uv sync --package dental-receptionist`).
3. **Docker networking: the agent shares the livekit container's network**
   (`network_mode: "service:livekit"`). Both see the same `127.0.0.1`, so audio works.
4. **Local vs Cloud:** the local values (`ws://127.0.0.1:7880`, `devkey`, `secret`) are set in
   `docker-compose.yml`. **Cloud** = add one small extra file, `docker-compose.cloud.yml`, which
   fills in the Cloud values from your `.env`. No code change.
5. **Console mode** runs on the Mac with `uv run python -m dental_receptionist.agent console`.
   Your `lk` (2.18.2) is older than the version `lk agent console` wants (2.18.8), so we call
   Python directly.

## Files that change

| File                                                               | New / changed | What it does                                                                                                                                                                                      |
| ------------------------------------------------------------------ | ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `agents/dental_receptionist/pyproject.toml`                      | new           | The agent's own package: `livekit-agents[openai,deepgram]~=1.8`, `python-dotenv`                                                                                                              |
| `agents/dental_receptionist/src/dental_receptionist/__init__.py` | new           | Makes it a Python package (empty)                                                                                                                                                                 |
| `agents/dental_receptionist/src/dental_receptionist/agent.py`    | new           | The agent: `INSTRUCTIONS`, `build_llm()`, `Receptionist(Agent)`, `AgentServer`, `entrypoint(ctx)`, `run_app` — every part commented                                                  |
| `agents/dental_receptionist/tests/test_dental_behavior.py`       | new           | 3 behavior tests (greeting, no invented hours, no fake booking). Skipped without `OPENAI_API_KEY`                                                                                               |
| `agents/dental_receptionist/tests/test_dental_joins_room.py`     | new           | Connection test: send the agent to a new local room → an AGENT participant joins. Skipped if the server or agent container is off. Copies the skip pattern from `tests/test_livekit_server.py` |
| `agents/dental_receptionist/Dockerfile`                          | new           | Based on the docs' uv template: Python 3.13 slim (Debian), non-root user, `uv sync --locked --no-dev --package dental-receptionist`, `CMD … start`                                           |
| `agents/dental_receptionist/README.md`                           | new           | How to run, talk to it (local + Cloud), and test it                                                                                                                                               |
| `.dockerignore`                                                  | new (root)    | Keeps `.env*`, `.venv`, tests, `.git`, `.claude` out of the image (docs template)                                                                                                         |
| `pyproject.toml` (root)                                          | changed       | Workspace (`agents/*`), depends on `dental-receptionist`, dev deps add `pytest-asyncio`, `asyncio_mode = "auto"`                                                                          |
| `uv.lock`                                                        | changed       | Updated by `uv add` / `uv lock`                                                                                                                                                               |
| `docker-compose.yml`                                             | changed       | New `dental_receptionist` service: build, `env_file` (optional), local LiveKit env, `network_mode: service:livekit`, waits for livekit to be healthy                                        |
| `docker-compose.cloud.yml`                                       | new           | Cloud switch: overrides the 3 `LIVEKIT_*` values with the ones from `.env`                                                                                                                    |
| `.env.example`                                                   | changed       | Comment only: the `LIVEKIT_*` lines in `.env` are used for Cloud mode; local values live in compose. No new key names                                                                         |
| `CLAUDE.md`                                                      | changed       | Commands section: start server + agent, the Cloud switch, console mode                                                                                                                            |
| `specs/dental_receptionist/001-first-agent/plan.md`              | new           | This plan; test output added at the end                                                                                                                                                           |

The agent code follows the docs quickstart shape ([voice-ai quickstart](https://docs.livekit.io/agents/start/voice-ai.md)), but with plugins:
`deepgram.STT(model="nova-3", language="en")`, `openai.responses.LLM(model="gpt-5.4-mini", reasoning=…low…)`,
`deepgram.TTS(model="aura-2-asteria-en")`, `TurnHandlingOptions(turn_detection=inference.TurnDetector(version="v1-mini"))`.
Before writing each line, I check the exact parameter names against the docs / plugin source.

## Order of work (tests first)

1. Save this plan as `specs/dental_receptionist/001-first-agent/plan.md`. **You** set its Status to `Approved`.
2. **Packages:** make the workspace + agent `pyproject.toml`. Then run
   `uv add --package dental-receptionist "livekit-agents[openai,deepgram]~=1.8" python-dotenv`
   and `uv add --dev pytest-asyncio`.
3. **Write the behavior tests first** and run them. They **fail** (there's no agent yet). This
   proves the tests can catch a missing or wrong agent.
4. **Write `agent.py`** and explain it part by part. Run the behavior tests again → **pass**.
5. **You:** quick check in console mode on the Mac (talk in the terminal).
6. **Docker:** `.dockerignore`, `Dockerfile`, compose service. Then `docker compose up -d --build`,
   and the logs should show the agent registered with the local server.
7. **Write the connection test** → run → pass.
8. **You:** real voice test, local: `lk token create … --agent dental-receptionist --open meet`.
9. **Cloud switch:** `docker-compose.cloud.yml`. **You:** same voice test against Cloud. Then switch back to local.
10. README, `.env.example` comment, `CLAUDE.md` commands.
11. Full test run, paste the real output into plan.md, Status `Built`. `Tested` only after you're happy.

## Risks

| Risk                                                                 | What we do                                                                                                                     |
| -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| Shared network trick fails (no audio in Docker)                      | Check `docker compose logs`. To find which half is broken, run the agent on the Mac in `dev` mode against the same server. |
| `uv sync --package` in Docker trips over the workspace lock        | Fix the Dockerfile copy steps. Last resort: the agent gets its own `uv.lock`                                                 |
| `gpt-5.4-mini` replies too slowly for voice                        | Lower the thinking setting further, or switch to `gpt-4.1-mini`                                                              |
| An LLM judge test is "random"                                        | Rerun once. If it keeps failing, make the *intent* clearer. Never weaken what we check                                       |
| Meet page can't reach `ws://localhost`                             | Use the example app from the infra test                                                                                        |
| The local turn detector needs model files or more memory in Docker   | Check the startup logs; add a download step to the Dockerfile if the docs/logs ask for one                                     |
| A `LIVEKIT_URL` set in your shell overrides `.env` in Cloud mode | README warns about it                                                                                                          |

## Proof (how we know it works)

- **Command:** `uv run pytest` (all) or `uv run pytest agents/dental_receptionist`
- **Tests:**
  - [x] `test_dental_behavior.py::test_greets_as_bright_smile` — "Hello" → a friendly Bright Smile Dental greeting that offers help (LLM judge)
  - [x] `test_dental_behavior.py::test_does_not_invent_hours` — "What time do you open?" → no specific hours made up
  - [x] `test_dental_behavior.py::test_does_not_book` — "Book me a cleaning" → says booking isn't available yet; doesn't claim to book
  - [x] `test_dental_joins_room.py::test_agent_joins_new_room` — dispatch to a fresh room on the local server → an AGENT participant appears within 20 s
  - [x] `test_dental_voice_speed.py::test_voice_arrives_fast_enough` — (added for the choppy-voice bug) middle of 3 tries: first sound < 1.0 s and faster than real time
  - [x] Existing `tests/test_hooks.py` + `tests/test_livekit_server.py` still pass
- **Manual checks (you):** console mode chat; local voice test with Meet (hear the greeting, 3-turn chat,
  watch `docker compose logs -f dental_receptionist`); the same voice test on Cloud.

## After building (filled in at the end)

### Test output (2026-11-22, Docker stack running, real run)

```text
$ uv run pytest -v agents/dental_receptionist
agents/dental_receptionist/tests/test_dental_behavior.py::test_greets_as_bright_smile PASSED
agents/dental_receptionist/tests/test_dental_behavior.py::test_does_not_invent_hours PASSED
agents/dental_receptionist/tests/test_dental_behavior.py::test_does_not_book PASSED
agents/dental_receptionist/tests/test_dental_joins_room.py::test_agent_joins_new_room PASSED
agents/dental_receptionist/tests/test_dental_voice_speed.py::test_voice_arrives_fast_enough PASSED
5 passed in 25.30s

$ uv run pytest            (whole repo, run 3 times)
33 passed in 27.04s
33 passed in 25.45s
33 passed in 25.81s
```

Red before green (tests first):
- Behavior tests before `agent.py` existed: `ModuleNotFoundError: No module named 'dental_receptionist.agent'`.
- Voice speed test with Deepgram's USA server: `first sound took 1.59s (limit 1.0s)`, 0.2x real time.
  After the 3-try change, re-checked against the USA server in memory: middle try 1.31 s → still FAILS, as it should.

Manual checks (by the user):
- Console mode: works; first try had choppy voice (→ Deepgram EU fix) and speaker→mic echo (→ use headphones).
- Local voice test, Meet + local server in Docker: greeting heard, voice clear, call ended cleanly.
- Cloud voice test (`docker-compose.cloud.yml`): agent registered at `wss://learning-….livekit.cloud`, joined `dental-cloud-1`, call ended cleanly. Switched back to local afterwards.

### What we changed from the plan, and why

1. **`livekit-api` dev dependency lowered to `>=1.2.0`** (was `>=2.0.1`): `livekit-agents 1.8` needs `livekit-api < 2`. The server tests still pass.
2. **Behavior tests open LiveKit's HTTP context** (an autouse fixture with `http_context.open()`): outside a real call, the OpenAI plugin has no web session. Test setup only; the agent is unchanged.
3. **No reasoning setting in `build_llm()`**: the OpenAI plugin already uses reasoning effort `"none"` for `gpt-5.4-mini`.
4. **Bug: choppy voice → Deepgram EU server.** Measured: the USA server's first sound took ~1.3 s and the voice came at 0.2–1.3x real time (stutter). EU: ~0.7–1.0 s, 1.4–1.8x. Added `build_stt()` / `build_tts()` with `DEEPGRAM_HOST = "api.eu.deepgram.com"`, plus a new test, `test_dental_voice_speed.py` (failing first, then passing).
5. **Speed test uses the middle of 3 tries** (user's choice): one try sat right at the 1.0 s limit and sometimes failed by bad luck. The same limits; it still fails against the USA server.
6. **Booking test intent clarified** (user's choice): the judge failed the agent for repeating the caller's own "next Monday". New wording: "does NOT suggest any new date or time of its own. Repeating the day the caller asked for is fine." Same rule, clearer.
7. **Plan approval:** Claude can't set `plan.md` to `Approved` (the safety check blocks it, because it opens the code gate). The user set it. Written into `specs/README.md` and `CLAUDE.md`.
8. **`.dockerignore` uses an allow list** (ignore everything, then allow `pyproject.toml`, `uv.lock`, `agents/`). Checked: no `.env*` files in the image.
