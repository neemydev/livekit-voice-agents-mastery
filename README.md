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

Docker setup comes with the first project.
