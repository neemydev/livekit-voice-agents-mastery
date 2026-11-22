# Dental receptionist (Bright Smile Dental)

A voice agent that answers calls for a dental clinic. Feature 001: it says hello first and chats
in short replies. It does **not** book anything or know clinic facts yet (later features).

Spec: [`specs/dental_receptionist/001-first-agent/`](../../specs/dental_receptionist/001-first-agent/)

| Part | Choice |
|---|---|
| Ears (STT) | Deepgram Nova-3, **EU server** (faster from our network) |
| Brain (LLM) | OpenAI `gpt-5.4-mini` |
| Mouth (TTS) | Deepgram Aura-2 (`asteria`), **EU server** |
| Turn detection | LiveKit `v1-mini`, runs locally on CPU |
| Server | Our local LiveKit server in Docker (default) or LiveKit Cloud |

Keys needed in the repo's `.env`: `OPENAI_API_KEY`, `DEEPGRAM_API_KEY`
(plus `LIVEKIT_*` for Cloud mode only). See `.env.example`.

## Run it

All commands run from the **repo root**.

```bash
docker compose up -d                              # LiveKit server + agent (local mode)
docker compose ps                                 # both "Up", livekit "healthy"
docker compose logs -f dental_receptionist        # watch the agent work
docker compose down                               # stop everything
```

After changing the code: `docker compose up -d --build dental_receptionist`.

## Talk to it

**Local server** (use a NEW room name each time; the "send the agent" note only works for a new room):

```bash
lk token create --url ws://localhost:7880 --api-key devkey --api-secret secret \
  --join --room dental-test-1 --identity patient \
  --agent dental-receptionist --open meet --valid-for 1h
```

**Quick check without any server** (talk in the terminal; wear headphones, or it hears itself):

```bash
uv run python -m dental_receptionist.agent console
```

## Switch to LiveKit Cloud

The same agent, no code change. Only the three `LIVEKIT_*` values change (taken from `.env`):

```bash
docker compose -f docker-compose.yml -f docker-compose.cloud.yml up -d dental_receptionist
lk token create --join --room dental-cloud-1 --identity patient \
  --agent dental-receptionist --open meet --valid-for 1h      # lk's default project = Cloud
docker compose up -d dental_receptionist                      # back to local
```

If `LIVEKIT_URL` is also set in your terminal (`export ...`), that value wins over `.env`.

## Tests

```bash
uv run pytest agents/dental_receptionist
```

| Test file | Checks | Needs |
|---|---|---|
| `test_dental_behavior.py` | greets as Bright Smile; doesn't invent hours; doesn't fake a booking | `OPENAI_API_KEY` |
| `test_dental_voice_speed.py` | voice arrives fast enough (first sound < 1 s, faster than real time) | `DEEPGRAM_API_KEY` |
| `test_dental_joins_room.py` | the agent in Docker joins a new room on the local server | `docker compose up -d` |

Tests whose needs are missing are **skipped**, not failed.

## If something goes wrong

| Symptom | Likely cause |
|---|---|
| Choppy, breaking voice; many `flush audio emitter due to slow audio generation` | Slow path to Deepgram. Run the speed test. We use the EU server for this reason |
| The agent talks to itself / stops mid-sentence (console mode) | Speakers → mic echo. Use headphones |
| No agent joins the room | Room name was already used, or the agent container isn't running (`docker compose ps`) |
| `transcript arrives after turn has been committed` | Ears a bit slow; turn tuning comes in course chapter 9 |
