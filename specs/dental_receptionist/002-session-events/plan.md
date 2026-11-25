# Plan: dental_receptionist 002 — see what the agent is doing (session events)

**Status:** `Built`   (built 2026-11-25; plan approved by user 2026-11-25)
**Project:** dental_receptionist · **Built from:** spec.md (Approved 2026-11-25) · Branch: `main` (branches paused)

## Context

During a call you can only **hear** the agent. Spec 002 adds "eyes" for you: one short log line for each
thing that happens (states, what was said, timing, why the call ended), plus telling Deepgram the clinic's name.
The caller hears no difference.

## What I found while checking (plan mode)

1. **Text-only tests DO fire agent events.** I ran one "Hello" turn with no microphone. Events seen:
   `agent_state_changed` (→ listening, → thinking, → speaking, → listening), `conversation_item_added`
   (user + assistant), and `close` (`user_initiated`). **Not** seen: `user_state_changed` and
   `user_input_transcribed`. They need a microphone (VAD and STT). → The session test can check agent states,
   `AGENT said` and `session closed`. The caller lines are proven by unit tests and the real call.
2. **The first `conversation_item_added` is not a chat message** (it's a config item). → We must skip anything that
   isn't a `ChatMessage`. Good thing we checked.
3. **Timing numbers are a dict on each reply** (`ChatMessage.metrics`). In the text test only `llm_node_ttft` was
   there (1.96 s). `e2e_latency` and `tts_node_ttfb` only exist in a real voice call. → Print whatever is present,
   skip what's missing, never crash.
4. **Docker logs are JSON.** In `start` mode LiveKit prints every log line as one JSON object (production style),
   and the `start` command has no option to change it. Our lines will be inside the `"message"` field.
   → We keep JSON (it's the right thing for production) and give you **one command** that shows only our lines
   as plain text, using `jq` (already on your Mac at `/usr/bin/jq`).
5. **`keyterm` works** on our installed Deepgram plugin: `deepgram.STT(..., keyterm=["Bright Smile Dental"])`.
6. Event classes import from `livekit.agents`: `AgentStateChangedEvent`, `UserStateChangedEvent`,
   `UserInputTranscribedEvent` (`transcript`, `is_final`), `ConversationItemAddedEvent` (`item`),
   `CloseEvent` (`reason` is an enum, e.g. `CloseReason.PARTICIPANT_DISCONNECTED`). Tests can build them directly.

## Files that change

| File                                                                  | New / changed | What it does                                                                                                                                                                                                                                            |
| --------------------------------------------------------------------- | ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `agents/dental_receptionist/src/dental_receptionist/call_logger.py` | new           | The call logger. Small **plain functions** make each line's text (easy to test). One function `attach_call_logger(session, room_name)` connects them to the session's events.                                                                   |
| `agents/dental_receptionist/src/dental_receptionist/agent.py`       | changed       | 1) `build_stt()` adds `keyterm=CLINIC_KEYTERMS` (`["Bright Smile Dental"]`). 2) In `entrypoint`, one line: `attach_call_logger(session, room_name=ctx.room.name)`, **before** `session.start(...)` so we also catch `initializing`. |
| `agents/dental_receptionist/tests/test_call_logger.py`              | new           | Unit tests (no network) + one text session test (OpenAI, skipped without key).                                                                                                                                                                          |
| `agents/dental_receptionist/tests/test_dental_stt.py`               | new           | Keyterm test: `build_stt()` has `"Bright Smile Dental"` as a keyterm (no network).                                                                                                                                                                  |
| `agents/dental_receptionist/README.md`                              | changed       | New "Watch a call" section with the `jq` command.                                                                                                                                                                                                     |
| `CLAUDE.md`                                                         | changed       | Commands: the "watch a call" command.                                                                                                                                                                                                                   |
| `specs/dental_receptionist/002-session-events/plan.md`              | new           | This plan (Draft → you set Approved), test output at the end.                                                                                                                                                                                          |

No Docker, compose, `.env.example` or dependency changes (logging and `jq` need nothing new).

### The call logger, in plain words

| Event                       | Function                     | Line it makes (example)                                                                                                                                 |
| --------------------------- | ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| (attach)                    | —                           | `[call] session started in room dental-test-7`                                                                                                        |
| `agent_state_changed`     | `describe_agent_state(ev)` | `[call] agent: thinking -> speaking`                                                                                                                  |
| `user_state_changed`      | `describe_user_state(ev)`  | `[call] user: speaking -> listening`                                                                                                                  |
| `user_input_transcribed`  | `describe_transcript(ev)`  | `[call] CALLER said: "Is this Bright Smile Dental?"` — **None** if partial or empty                                                            |
| `conversation_item_added` | `describe_reply(ev)`       | `[call] AGENT said: "Yes, how can I help?"` — **None** if not a `ChatMessage` or not the assistant                                           |
| (same reply)                | `describe_timing(metrics)` | `[call] timing: replied 0.84 s after you stopped (llm first word 0.41 s, voice first sound 0.22 s)` — only the parts present; **None** if none |
| `close`                   | `describe_close(ev)`       | `[call] session closed: participant_disconnected` (+ the error, if any)                                                                               |

- Logger name `dental_receptionist.call`, level INFO. LiveKit's setup sends it to Docker's output with everything else.
- Handlers are plain `def`, quick: build the text, log it, done.
- Why caller text comes from `user_input_transcribed` (final only) and agent text from `conversation_item_added`:
  that's the lesson's split, and it avoids logging the caller twice.

## Order of work (tests first)

1. Save this plan as `specs/dental_receptionist/002-session-events/plan.md`, Status `Draft`. **You** set it to `Approved`.
2. **Write the tests first** (`test_call_logger.py`, `test_dental_stt.py`). Run them → **red** (no `call_logger` yet, no keyterm).
3. **Write `call_logger.py`**, explained part by part. Run the unit tests → green.
4. **Change `agent.py`**: keyterm + the one `attach_call_logger` line. Run all dental tests → green.
5. **Docker:** `docker compose up -d --build dental_receptionist`; logs show the agent registered.
6. **You:** paste your paper prediction into intent.md (if not done yet).
7. **You: real call.** Terminal 1: the watch command. Terminal 2: `lk token create … --agent dental-receptionist --open meet`.
   Say "Hi, is this Bright Smile Dental?", then ask about Dr. Chen, then hang up.
   Compare the lines with your prediction; check the spelling of "Bright Smile Dental".
8. README "Watch a call" + CLAUDE.md command.
9. Full `uv run pytest`, paste the real output into plan.md, Status `Built`. `Tested` after you're happy.

## The "watch a call" command (goes in README + CLAUDE.md)

```bash
docker compose logs -f --no-log-prefix dental_receptionist \
  | jq -R -r 'fromjson? | select((.message // "") | startswith("[call]")) | .message'
```

`-R` reads each line as text, `fromjson?` turns it into JSON (and quietly skips lines that aren't JSON),
`select(...)` keeps only our `[call]` lines, `.message` prints just the text.

## Risks

| Risk                                                             | What we do                                                                                                                            |
| ---------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| Our lines don't show in Docker (logger level)                    | LiveKit sets the root logger to INFO and our logger inherits it; check in step 5. If missing, set the level on our logger explicitly. |
| `e2e_latency` / `tts_node_ttfb` missing in the real call too | The timing line prints what's there; we note it in plan.md and look in the docs.                                                      |
| A handler error breaks the call                                  | Handlers only format strings; unit tests cover missing fields.                                                                        |
| Text session test is flaky (LLM)                                 | It only checks that lines **exist**, not what the agent said.                                                                   |
| Deepgram still misspells the name                                | Try once more; if it keeps happening, note it — more keyterms are a later decision (spec).                                           |
| The keyterm test reads a private field (`stt._opts.keyterm`)   | Acceptable for a learning project; comment says why. If LiveKit renames it, the test tells us.                                        |

## Proof (how we know it works)

- **Command:** `uv run pytest agents/dental_receptionist` (this agent) and `uv run pytest` (everything).
- **Tests:**
  - [ ] `test_call_logger.py::test_agent_state_line` — `thinking → speaking` makes `[call] agent: thinking -> speaking`
  - [ ] `test_call_logger.py::test_user_state_line` — `speaking → listening` makes the user line
  - [ ] `test_call_logger.py::test_final_transcript_line` — final text makes `CALLER said: "..."`
  - [ ] `test_call_logger.py::test_partial_transcript_makes_no_line` — partial → `None`
  - [ ] `test_call_logger.py::test_agent_reply_line` — assistant `ChatMessage` makes `AGENT said: "..."`
  - [ ] `test_call_logger.py::test_non_message_item_makes_no_line` — user message / non-message → `None`
  - [ ] `test_call_logger.py::test_timing_line_full` — all 3 numbers → the full timing line
  - [ ] `test_call_logger.py::test_timing_line_partial_and_empty` — only `llm_node_ttft` → short line; none → `None`
  - [ ] `test_call_logger.py::test_close_line` — `participant_disconnected` makes `session closed: participant_disconnected`
  - [ ] `test_call_logger.py::test_logger_in_text_session` — (OpenAI) one "Hello" turn with the logger attached →
    logs contain `session started`, `agent: thinking -> speaking`, `AGENT said:`, `session closed`
  - [ ] `test_dental_stt.py::test_stt_knows_clinic_name` — `build_stt()` has `"Bright Smile Dental"` as keyterm
  - [ ] All 001 tests and the infra/hook tests still pass (33 today → 44 expected)
- **Manual (you):** real local call with the watch command; compare with your prediction; check the name spelling.

## After building (filled in at the end)

### Red before green
- `test_call_logger.py` → `ModuleNotFoundError: No module named 'dental_receptionist.call_logger'`
- `test_dental_stt.py` → `AssertionError` (keyterm list had no "Bright Smile Dental")

### Test output (2026-11-25)

```text
$ uv run pytest agents/dental_receptionist/tests/test_call_logger.py -q -s
[call] session started in room test-room
[call] agent: initializing -> listening
[call] agent: listening -> thinking
[call] agent: thinking -> speaking
[call] AGENT said: "Hello, thanks for calling Bright Smile Dental. How can I help you today?"
[call] timing: llm first word 2.00 s
[call] agent: speaking -> listening
[call] session closed: user_initiated
10 passed in 7.73s

$ uv run pytest            (Docker stack running)
tests/test_hooks.py .........................                            [ 93%]
tests/test_livekit_server.py ...                                         [100%]
============================= 44 passed in 34.29s ==============================
```

### Docker check
- `docker compose up -d --build dental_receptionist` → `registered worker`.
- `test_dental_joins_room.py` passed, and the watch command showed `[call]` lines from the container
  (`session started in room pytest-dental-…`, `agent: initializing -> listening`). Logger level was fine; no change needed.

### Real call (user, local server + Meet, room `dental-test-20`)

```text
10:47:41 [call] session started in room dental-test-20
10:47:41 [call] agent: initializing -> listening
10:47:41 [call] agent: listening -> thinking
10:47:43 [call] agent: thinking -> speaking
10:47:48 [call] AGENT said: "Hello, this is Bright Smile Dental. How can I help you today?"
10:47:48 [call] timing: llm first word 2.03 s, voice first sound 0.30 s
10:47:48 [call] agent: speaking -> listening
10:48:03 [call] user: listening -> away
10:48:05 [call] user: away -> speaking
10:48:07 [call] user: speaking -> listening
10:48:08 [call] user: listening -> speaking
10:48:15 [call] user: speaking -> listening
10:48:30 [call] user: listening -> away
10:49:32 [call] user: away -> speaking
10:49:35 [call] user: speaking -> listening
10:49:35 [call] CALLER said: "Can you hear me?"
10:49:35 [call] user: listening -> speaking
10:49:37 [call] user: speaking -> listening
10:49:37 [call] agent: listening -> thinking
10:49:37 [call] user: listening -> speaking
10:49:38 [call] agent: thinking -> listening
10:49:38 [call] user: speaking -> listening
10:49:40 [call] agent: listening -> thinking
10:49:40 [call] agent: thinking -> speaking
10:49:43 [call] AGENT said: "Yes, I can hear you. How can I help?"
10:49:43 [call] timing: replied 3.71 s after you stopped (llm first word 2.49 s, voice first sound 0.39 s)
10:49:43 [call] agent: speaking -> listening
10:49:58 [call] user: listening -> away
10:50:40 [call] session closed: participant_disconnected
```

The logger works: every kind of line appeared, including `away` and the close reason. It also showed two **problems**
that were hidden before (not caused by the logger; to investigate as their own bug fixes, test first):

1. **Slow brain:** LLM first word 2.03 s and 2.49 s. The whole reply came 3.71 s after the caller stopped
   (budget: ~0.5 s). The voice (0.30-0.39 s) is fine.
2. **Lost speech:** at 10:48:05-07 and 10:48:08-15 VAD heard the caller speak (~9 s), but STT gave **no** final text,
   so the agent never answered. Only "Can you hear me?" (10:49:35) was transcribed.
   **Cause (user, 2026-11-25): a noisy room.** VAD reacts to any voice-like sound, so background noise counted as
   "speaking", but there were no clear words for STT to write down. Not a code bug; no change. The real fix for this is
   noise cancellation (course ch. 7, a later feature).

Still to check by hand: the spelling of "Bright Smile Dental" in a `CALLER said` line (not said successfully in this call),
and the user's prediction vs. the real lines.

### What we changed from the plan, and why
- Nothing in the code. The watch command got `--since 1s` for live calls, so old lines from earlier tests are hidden.
