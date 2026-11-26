# Plan: dental_receptionist 003 — switch the brain to gpt-6-luna (thinking off)

**Status:** Tested   (tested by user in a real call 2026-11-26; built 2026-11-25; small fix: plan only)
**Project:** dental_receptionist · **Date:** 2026-11-25 · Branch: `main` (branches paused)

## Context

The call logger (spec 002) showed the brain is slow: 2.03 s and 2.49 s to the first word in a real call
(budget ~0.5 s). The user chose to switch to `gpt-6-luna` with hidden "thinking" (reasoning) switched off.

Measured before deciding (scratchpad script, same LiveKit plugin, one brain reused 4 times like a call):

| Model                                           | 1st question     | Later questions (middle) |
| ----------------------------------------------- | ---------------- | ------------------------ |
| `gpt-5.4-mini`, thinking off (before)         | 1.82 s           | 0.86 s                   |
| `gpt-6-luna`, default thinking                | 2.14 s           | 1.31 s                   |
| **`gpt-6-luna`, thinking off (chosen)** | **1.28 s** | **0.67 s**         |

Why "thinking off" must be written by us: the plugin turns thinking off by itself only for models it knows
(`gpt-5.4-mini`, `gpt-5.6-luna`, ...). `gpt-6-luna` is newer than our plugin version, so without our setting
OpenAI's default thinking stays on (slower).

## Files that change

| File                                                            | Change                                                                                                        |
| --------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| `agents/dental_receptionist/src/dental_receptionist/agent.py` | `LLM_MODEL = "gpt-6-luna"`; `build_llm()` passes `reasoning=Reasoning(effort="none")`; comments updated |

Nothing else. The behavior tests use `build_llm()`, so they will use luna automatically.

## Order of work

1. Save this plan (Draft). **User** sets it to `Approved`.
2. Change `agent.py`.
3. Rebuild the container: `docker compose up -d --build dental_receptionist`.

## Proof

- **No new tests**, by the user's choice (2026-11-25): "just change the model, no need to test".
- Not proven yet: the first reply is still ~1.3 s (connection setup), and the real call's 2.49 s may have
  other causes. Left for later if the user wants.
- The user tries it in a real call; the `[call] timing` lines show the new numbers. Then `Tested`.

## After building

- `agent.py` changed as planned (`gpt-6-luna`, `reasoning=Reasoning(effort="none")`, import from `openai.types.shared_params`).
- `docker compose up -d --build dental_receptionist` → `registered worker`.
- No tests run (user's choice). Real-call timing: to be added after the user's call.
