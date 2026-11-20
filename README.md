# LiveKit Voice Agents Mastery

Learning to build real-time voice AI agents with [LiveKit Agents](https://docs.livekit.io/agents/),
by building four projects from scratch.

| Project | What it is | Status |
|---|---|---|
| `agents/dental_receptionist/` | A voice receptionist for a dental clinic | Not started |
| `agents/restaurant/` | A multi-agent restaurant system (greeting, ordering, ...) | Not started |
| `agents/healthcare/` | A healthcare voice agent | Not started |
| `agents/contact_center/` | An AI contact center | Not started |

Course followed: [LiveKit Academy](https://www.livekit-academy.com/courses).

## How this repo is built

Every feature is planned before it is coded, following Anthropic's
[AI-native SDLC playbook](https://claude.com/resources/articles/the-ai-native-sdlc-playbook):

1. `intent.md` - what and why
2. `spec.md` - how it must behave
3. `plan.md` - files, order of work, and the tests that prove it works
4. Code + tests

All plans live in [`specs/`](specs/). The learning diary is in [`progress/log.md`](progress/log.md).

## Run it

Requirements: Python 3.13, [uv](https://docs.astral.sh/uv/), Docker.

```bash
cp .env.example .env      # then fill in your own keys
uv sync                   # install dependencies
uv run pytest             # run the tests
```

## Local LiveKit server

A self-hosted LiveKit server runs in Docker, so no LiveKit Cloud account is needed while learning.
Settings: [`infra/livekit/livekit.yaml`](infra/livekit/livekit.yaml). Spec: [`specs/infra/001-local-livekit-server/`](specs/infra/001-local-livekit-server/).

```bash
docker compose up -d              # start it
docker compose ps                 # check: should say "healthy"
curl http://localhost:7880        # check: prints "OK"
docker compose logs -f livekit    # watch participants and tracks arrive
docker compose down               # stop it
```

Connect with: URL `ws://localhost:7880`, API key `devkey`, API secret `secret`.
These dev keys are public - fine on your own computer, never on a server on the internet.

**Try real media** (needs the [LiveKit CLI](https://docs.livekit.io/intro/basics/cli.md), `lk`):

```bash
# 1. A demo bot joins room "my-first-room" and streams a demo video
lk room join --url ws://localhost:7880 --api-key devkey --api-secret secret \
  --identity demo-bot --publish-demo my-first-room

# 2. In another terminal, make a token for yourself
lk token create --api-key devkey --api-secret secret \
  --join --room my-first-room --identity you --valid-for 24h
```

Then open <https://meet.livekit.io/?tab=custom>, enter `ws://localhost:7880` and your token, and join.
You should see the bot's video.
