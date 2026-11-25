# Spec: See what the agent is doing during a call (session events)

**Status:** Approved  <!-- Draft → Approved --> (approved by user 2026-11-25)
**Date:** 2026-11-25
**Built from:** intent.md (Approved 2026-11-25)

> Stage 2 — DESIGN. What the agent must do and how it should behave.

## The big picture

```text
  call in Meet ──audio──▶ AgentSession (our agent, in Docker)
                              │  fires events while it runs
                              ▼
                     our "call logger" (small, quick functions)
                              │  one short line per event
                              ▼
               docker compose logs -f dental_receptionist   ◀── you watch here
```

The caller hears **no difference**. We only add "eyes" for the developer.

## Sample log (what you should see for one short call)

Times and exact words will differ. This shows the **kind** of lines, not the exact format.

```text
[call] session started in room dental-test-7
[call] agent: initializing -> listening
[call] agent: listening -> thinking
[call] agent: thinking -> speaking
[call] AGENT said: "Hello, thank you for calling Bright Smile Dental! How can I help you today?"
[call] agent: speaking -> listening
[call] user: listening -> speaking
[call] user: speaking -> listening
[call] CALLER said: "Hi, is this Bright Smile Dental?"
[call] agent: listening -> thinking
[call] agent: thinking -> speaking
[call] AGENT said: "Yes, this is Bright Smile Dental. How can I help?"
[call] timing: replied 0.84 s after you stopped (llm first word 0.41 s, voice first sound 0.22 s)
[call] agent: speaking -> listening
[call] session closed: participant_disconnected
```

(The exact order of the first few state lines is something we find out in the real call. That's the point
of your prediction.)

## Must do

**Logging (the new behavior)**
- [ ] Log every **agent state** change, as `old -> new` (`initializing`, `idle`, `listening`, `thinking`, `speaking`).
- [ ] Log every **user state** change, as `old -> new` (`speaking`, `listening`, `away`).
- [ ] Log what the **caller said**: **final** transcripts only, never the partial ones.
- [ ] Log what the **agent said**: the text of each agent reply, once it's added to the conversation.
- [ ] Log **timing** for each agent reply that answers the caller: how long from "you stopped talking" to
      "agent started talking" (`e2e_latency`), plus the two biggest parts: LLM first word (`llm_node_ttft`)
      and voice first sound (`tts_node_ttfb`). Use the numbers LiveKit already measures. Don't build our own timer.
      If a number is missing (for example, the greeting has no "you stopped talking"), skip it, don't crash.
- [ ] Log when the session **closes**, and the **reason** (for example `participant_disconnected`).
- [ ] Every line starts with the same short tag (e.g. `[call]`), so it's easy to find in the logs.
- [ ] Use Python's `logging` (not `print`), so lines appear in `docker compose logs` with the other agent logs.
- [ ] Event handlers stay **quick**: they only format and log a line. No network calls, no waiting.

**Hearing the clinic's name**
- [ ] Tell Deepgram about the clinic name: `keyterm=["Bright Smile Dental"]` (Nova-3's setting; not the old `keywords`).

**Nothing else changes**
- [ ] Same models, same instructions, same greeting, same Docker setup, same Cloud switch.
- [ ] All 001 tests still pass.

**Code shape (so it's easy to read and to test)**
- [ ] The logging lives in its own small part (for example a `call_logger.py` with one function that attaches
      all handlers to a session). `agent.py` gets just one extra line to turn it on.
- [ ] The text of each log line is made by small plain functions, so a test can check them without a call.

**Proof (tests)**
- [ ] **Unit tests, no network:** given a state change / transcript / reply / close event, the right line is made.
      Partial transcripts make **no** line. Missing timing numbers don't crash.
- [ ] **Session test, text only** (calls OpenAI, tiny cost, skipped without the key): run one turn ("Hello")
      in a text-only `AgentSession` with the logger attached → the logs contain an `AGENT said:` line.
- [ ] **Keyterm test, no network:** `build_stt()` is set up with `"Bright Smile Dental"` as a keyterm.
- [ ] **Real call (by hand, results in plan.md):** local server + Meet + `docker compose logs -f dental_receptionist`.
      Compare the logs with **your prediction** in intent.md. Say "Bright Smile Dental" and check the spelling.

## Nice to have

- [ ] A one-line summary when the call ends: number of turns and the average reply time.
- [ ] The README gets a short "Watch a call" section.

## Not in this version (out of scope)

- Saving transcripts or reports to a file or database (later, with Postgres).
- Sending states to a web page (later, "Agent Frontends" course).
- Cost / token usage per call (`session_usage_updated`).
- Changing turn detection or VAD settings (course ch. 9).
- More keyterms (only if the logs show a mistake).

## Parts we will use

| Part | Choice | Why |
|---|---|---|
| Speech-to-text (ears) | Deepgram `nova-3`, EU server, **+ `keyterm=["Bright Smile Dental"]`** | Same as 001, now helped with the clinic name |
| LLM (brain) | `gpt-5.4-mini` (unchanged) | Already fast enough |
| Text-to-speech (voice) | Deepgram Aura-2 (unchanged) | Already fast enough |
| VAD | The session's built-in Silero VAD (unchanged, automatic in 1.8) | Drives the user states we log |
| Turn detection | `TurnDetector(v1-mini)` (unchanged) | Decides when "thinking" starts |
| Events | `agent_state_changed`, `user_state_changed`, `user_input_transcribed`, `conversation_item_added`, `close` | The four from the lesson, plus `close` for the end reason |
| Timing | `ChatMessage.metrics` on agent replies: `e2e_latency`, `llm_node_ttft`, `tts_node_ttfb` | Measured by LiveKit already; the docs' recommended way |
| Logging | Python `logging` | Shows up in Docker logs; the docs recommend it over `print` |

## What the docs say

- [Events and error handling](https://docs.livekit.io/reference/agents/events.md): each handler gets **one event object**.
  `agent_state_changed` / `user_state_changed` have `old_state` and `new_state`. Agent states: `initializing`, `idle`,
  `listening`, `thinking`, `speaking`. User states: `speaking`, `listening`, `away` (default 15 s).
  `user_input_transcribed` has `transcript` and `is_final`. `conversation_item_added` has `item` (a `ChatMessage`
  with `role` and `text_content`). `close` has `reason` (e.g. `participant_disconnected`, `job_shutdown`) and `error`.
- [Data hooks: per-turn latency](https://docs.livekit.io/testing/observability/data.md#per-turn-latency): every `ChatMessage` has
  `metrics`. Agent messages: `e2e_latency` (you stopped → agent began), `llm_node_ttft`, `tts_node_ttfb`. Example reads
  them in `conversation_item_added`. The docs say: in production use Python `logging`, not `print`.
- [Silero VAD](https://docs.livekit.io/agents/logic/turns/vad.md): VAD drives turn-taking and user speech detection.
  Our installed 1.8 code: `AgentSession` uses the bundled Silero VAD by default (`inference.VAD(model="silero")`).
- [Turns overview](https://docs.livekit.io/agents/logic/turns.md): turn detection sits on top of VAD; endpointing waits
  between `min_delay` and `max_delay` after speech before ending the turn.
- [Deepgram STT](https://docs.livekit.io/agents/models/stt/deepgram.md): `keyterm` (str or list) boosts terms on **Nova-3**;
  `keywords` with weights is for Nova-2 only. Installed plugin has `keyterm` (checked).
- Course: [Voice AI Foundations, ch. 3](https://www.livekit-academy.com/courses/voice-ai-foundations/understanding-agent-session):
  same four events and states. Its code is older (handlers take `state: str`, `MultimodalModel`, `keywords`, `silero.VAD.load()` required).
  We follow the current docs instead.

## Concerns

1. **Do state events fire in a text-only test?** A text test has no microphone or speaker, so user states (from VAD)
   won't fire, and agent states may not either. So the session test only checks the `AGENT said:` line, and the state
   lines are proven by the unit tests plus the real call. To confirm in the plan.
2. **Log format in Docker.** In `start` mode the agent may print logs as JSON, not plain text. If our lines are hard
   to read, the plan finds the right setting (docs first). To check in the plan.
3. **Privacy.** We will log what callers say. That's fine for local testing with our own voice. A real clinic would need
   rules for this (patient data). Not a problem now, but worth knowing.
4. **The greeting has no timing.** `e2e_latency` measures from "you stopped talking", and the greeting comes before you
   say anything. So the first reply shows no timing line. That's expected, not a bug.
5. **Keyterm can't be fully proven by a test.** A test can check the setting is passed. Whether Deepgram then spells it
   right is only proven by the real call.
