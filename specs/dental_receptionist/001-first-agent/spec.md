# Spec: First dental receptionist agent (greet and chat)

**Status:** Approved  <!-- Draft → Approved --> (approved by user 2026-11-22)
**Date:** 2026-11-22
**Built from:** intent.md (Approved 2026-11-22)

> Stage 2 — DESIGN. What the agent must do and how it should behave.

## The big picture (diagram)

```text
  YOUR MAC                                 DOCKER  (both containers share ONE network,
                                                    so "127.0.0.1" means the same place)
 ┌───────────────────────────┐            ┌───────────────────────────────────────────┐
 │ Browser: LiveKit Meet     │            │  livekit (SFU)          :7880 :7881 :7882  │
 │  mic + speaker            │◀══ audio ═▶│   room "dental-test-1"                     │
 │  (you = the patient)      │            │    ├ participant: patient (you)            │
 └───────────────────────────┘            │    └ participant: agent  ◀──┐             │
 ┌───────────────────────────┐            │                             │             │
 │ Terminal: lk token create │──token────▶│  dental_receptionist (our agent)          │
 │  --agent dental-...       │ (+ "send   │   AgentServer → entrypoint → AgentSession  │
 │  --open meet              │  the agent")│   ears: Deepgram  brain: OpenAI  mouth:   │
 └───────────────────────────┘            │   Deepgram   turn detector: v1-mini (CPU)  │
                                          └──────────────────────┬────────────────────┘
                                                                 │ internet (HTTPS/WSS)
                                                                 ▼
                                                    Deepgram API      OpenAI API

  Cloud mode (switch by settings, no code change): the agent connects to
  wss://learning-….livekit.cloud instead of the local livekit container.
```

## Sample conversation

> **You:** `docker compose up -d` → the `livekit` and `dental_receptionist` containers start.
> **You:** `lk token create ... --room dental-test-1 --agent dental-receptionist --open meet`
> **Browser:** Meet opens and joins room `dental-test-1`. LiveKit creates the room and sends the agent in.
>
> **Agent:** "Hello, thank you for calling Bright Smile Dental! How can I help you today?"
> **Patient:** "Hi, I'd like to book a cleaning."
> **Agent:** "I'd love to help, but I can't book appointments just yet. Is there anything else I can do for you?"
> **Patient:** "What time do you open tomorrow?"
> **Agent:** "Sorry, I don't have our opening hours yet. Please call back soon and we'll be able to check for you."
> **Patient:** "Okay, thanks, bye!"
> **Agent:** "You're welcome. Have a lovely day!"
>
> **You:** close the tab → the room has no people left → it closes, and the agent's job ends.

## Must do

**The agent (behavior)**
- [ ] Says hello **first**, as the receptionist of **Bright Smile Dental**.
- [ ] Replies in a friendly way, **short: 1–2 sentences**. Plain words, no lists or emojis (it is spoken).
- [ ] Speaks **English** only.
- [ ] **Does not make up clinic facts** (hours, prices, free slots). It says it can't check that yet.
- [ ] **Does not book** anything. It says booking isn't available yet.

**The code**
- [ ] Our own agent code in `agents/dental_receptionist/` (not `lk agent init`), with the parts we learned:
      `AgentServer`, `@server.rtc_session(agent_name="dental-receptionist")`, `entrypoint(ctx)`,
      `AgentSession`, a `Receptionist(Agent)` class, `session.start(...)`, `generate_reply(...)`.
      Every part has a short comment that says what it does.
- [ ] Pipeline with **plugins and our own keys**:
      ears = Deepgram STT (Nova-3, English), brain = a small OpenAI model, mouth = Deepgram TTS (Aura-2).
- [ ] Turn detection pinned to the **local `v1-mini`** model (runs on CPU, free, no LiveKit Cloud needed).
- [ ] Keys load from `.env` with python-dotenv. Any new key **names** go in `.env.example` (empty values).

**Running it**
- [ ] Runs in **Docker**: a Dockerfile for the agent and a `dental_receptionist` service in `docker-compose.yml`.
      `docker compose up -d` starts the server **and** the agent.
- [ ] **Default = local server.** The agent connects to the local `livekit` container with `devkey` / `secret`.
- [ ] **Cloud switch by settings only, no code change.** One documented command runs the same agent
      against LiveKit Cloud (project "Learning") using the Cloud keys in `.env`.
- [ ] **Quick check without a server:** console mode on the Mac (`console`), to talk in the terminal.
      (Console mode needs the Mac's mic, so it runs on the Mac, not in Docker.)
- [ ] A short "how to run / how to talk to it / how to switch to Cloud" section in a README.

**Proof (tests)**
- [ ] **Behavior tests** (pytest, text only, no server needed; they call OpenAI):
      1. "Hello" → a friendly Bright Smile Dental greeting that offers help.
      2. "What time do you open?" → does **not** invent hours.
      3. "I want to book a cleaning" → says booking isn't available yet; doesn't pretend to book.
- [ ] **Connection test** (pytest, skipped if the Docker stack is off): ask the local server to send
      the agent into a new room → the agent joins that room within a few seconds.
- [ ] **Real voice test** (by hand, results written in plan.md): local server + Meet. You hear the greeting
      and have a 3-turn chat. Then the same against **Cloud**.

## Nice to have

- [ ] A tiny helper (script or Make-style command) for "new test room + token + open Meet".
- [ ] Watch the agent's logs (`docker compose logs -f dental_receptionist`) during a call and see
      the steps: job received → session started → user said / agent said.

## Not in this version (out of scope)

- Real clinic facts, tools, checking availability, booking (later features, course ch. 4–6).
- Our own web frontend / own Agent Console / FastAPI backend (later, with "Agent Frontends").
- Phone calls (SIP), noise cancellation, recording.
- LiveKit Inference, deploying to LiveKit Cloud (`lk agent deploy`).
- Other languages.

## Parts we will use

| Part | Choice | Why |
|---|---|---|
| Speech-to-text (ears) | Deepgram plugin, `nova-3`, `en` | You have the key; plugin default; built for live audio |
| LLM (brain) | OpenAI plugin, `openai.responses.LLM(...)`, a small current model (exact name in plan) | You have the key; the docs recommend the Responses API; small = cheap + fast |
| Text-to-speech (voice) | Deepgram plugin, `TTS`, an Aura-2 voice (e.g. `aura-2-asteria-en`) | Same company as STT (2 keys total); made for fast live speech |
| Turn detection | `inference.TurnDetector(version="v1-mini")` + the session's built-in VAD | Runs locally, free; the default full model would need LiveKit Cloud keys |
| Agent framework | `livekit-agents[openai,deepgram]~=1.8` (turn detector built in from 1.8.12) | Current major version in the docs |
| Server | Our local `livekit/livekit-server:v1.13.11` (spec infra/001) | Intent: self-hosting by default |
| Container | Dockerfile based on the docs' uv template, Python 3.13 (matches the repo) | Project rule: everything in Docker |
| Talk to it | `lk token create --agent … --open meet` (lk 2.18.2 has both flags) | Ready-made web client; no frontend to build yet |
| Tests | pytest + pytest-asyncio, LiveKit's `session.run()` + `judge()`, `livekit-api` for dispatch | The docs' testing tools |

## What the docs say

- [Voice AI quickstart](https://docs.livekit.io/agents/start/voice-ai.md): current agent shape — `AgentServer`, `@server.rtc_session(agent_name=…)`, `entrypoint(ctx: JobContext)`, `session.start(room=ctx.room, agent=…)`, `generate_reply(...)`, `agents.cli.run_app(server)`.
- [Startup modes](https://docs.livekit.io/agents/server/startup-modes.md): `console` runs in the terminal **without connecting to LiveKit**; `dev` auto-reloads; `start` is for production.
- [Job lifecycle](https://docs.livekit.io/agents/server/job.md): each call runs in its own process; the job runs until all non-agent participants leave.
- [Agent dispatch](https://docs.livekit.io/agents/server/agent-dispatch.md): with `agent_name` set, the agent is only sent when asked — via token (`lk token create --agent …`, only when the room is **new**) or via API (`lk dispatch create`). The room is created automatically if it doesn't exist.
- [Connecting to LiveKit](https://docs.livekit.io/intro/basics/connect.md): a room is created when the first participant joins and closed when the last non-agent leaves; self-hosted dev URL is `ws://localhost:7880`.
- [Models overview](https://docs.livekit.io/agents/models.md): plugins are optional extras, e.g. `uv add "livekit-agents[openai]~=1.8"`.
- [Deepgram STT](https://docs.livekit.io/agents/models/stt/deepgram.md): `deepgram.STT(model="nova-3", language="en")`, key `DEEPGRAM_API_KEY`.
- [Deepgram TTS](https://docs.livekit.io/agents/models/tts/deepgram.md): `deepgram.TTS(model="aura-2-asteria-en")` for Aura voices.
- [OpenAI LLM](https://docs.livekit.io/agents/models/llm/openai.md): use `openai.responses.LLM(model=…)` for direct OpenAI; key `OPENAI_API_KEY`.
- [Turn detector](https://docs.livekit.io/agents/logic/turns/turn-detector.md): the default full `v1` model runs on LiveKit Inference and authenticates with LiveKit **Cloud** keys; `v1-mini` runs locally on CPU, free; pin it with `version="v1-mini"`. Uses about 310–340 MB of memory.
- [LiveKit Inference](https://docs.livekit.io/agents/models/inference.md): uses your LiveKit Cloud key and secret — why we don't use it with the local server.
- [Unit tests](https://docs.livekit.io/testing/unit-tests.md): `pytest` + `pytest-asyncio`; `session.run(user_input=…)`; `result.expect.next_event().is_message(role="assistant").judge(llm, intent=…)`.
- [Builds and Dockerfiles](https://docs.livekit.io/deploy/agents/builds.md): uv-based template; glibc image (not Alpine); non-root user; copy `pyproject.toml` + `uv.lock` first; never copy `.env*` into the image; `CMD [... "start"]`.
- [Agent Console](https://docs.livekit.io/testing/agent-console.md): a LiveKit Cloud page; for local rooms we use Meet instead.
- `lk token create --help` (lk 2.18.2): `--agent` dispatches an agent, `--open meet|console` opens a web app.
- Course: [Voice AI Foundations, ch. 2](https://www.livekit-academy.com/courses/voice-ai-foundations/project-setup) — same agent parts; the course uses Cloud + `lk agent init`, we deliberately build it ourselves on the local server.

## Concerns

1. **Docker networking (flagged in infra spec, concern 2).** Our server tells every client "send media to
   `127.0.0.1`". Inside a *separate* agent container, `127.0.0.1` would mean the agent container itself,
   so audio would fail. **Proposed fix:** the agent container **shares the livekit container's network**
   (Compose `network_mode: "service:livekit"`). Then `127.0.0.1` means the same place for both, and the
   agent connects to `ws://127.0.0.1:7880`. Side effect: the livekit container must be running even in
   Cloud mode. We prove it with the connection test and the real voice test.
2. **`.env` now holds the Cloud `LIVEKIT_*` values, but the default must be local.** The local settings
   (`ws://127.0.0.1:7880`, `devkey`, `secret`) will be set in `docker-compose.yml`, which wins over `.env`.
   Cloud mode = a second, small compose file (or similar) that uses the `.env` values instead. Exact method in the plan.
3. **`lk` CLI is pointed at Cloud by default** (3 Cloud project entries, default `livekitlearning`).
   For local tokens we must pass the local URL and dev keys (or add a "local" project to `lk`). Easy to mix up — the README will show both.
4. **Meet + local server is not proven yet.** `--open meet` opens an `https://` page that connects to `ws://localhost`.
   This worked with the example app in the infra test, so it should work here too. If not, we use that example app.
5. **The OpenAI model name.** Several small OpenAI models are being retired (for example `gpt-4.1-mini` on Inference
   in January 2027). In the plan we pick a current small model and confirm it works with your key.
6. **Behavior tests call OpenAI on every run** (tiny cost), and an LLM judge can be a bit "random". We keep the
   intents simple and the test count small. They are skipped if `OPENAI_API_KEY` isn't set.
7. **Repo layout for Python packages + Docker.** The repo has one root `pyproject.toml`/`uv.lock`. The agent's image
   should contain only the agent's packages. Options: a uv **workspace** (root + one member per agent) or a separate
   `pyproject.toml` inside `agents/dental_receptionist/`. Decide in the plan.
8. **v1-mini on CPU.** It needs ~330 MB RAM and some CPU per job. Fine for one or two test calls in Docker Desktop.
9. **Different from the course on purpose:** the course uses Cloud + Inference + `lk agent init`.
   The *code ideas* are the same, so the lessons still match.
