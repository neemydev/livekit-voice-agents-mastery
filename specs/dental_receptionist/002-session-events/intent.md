# Intent: See what the agent is doing during a call (session events)

**Status:** Approved  <!-- Draft → Approved --> (approved by user 2026-11-25)
**Author:** neemydev (drafted by Claude at the user's request: "go ahead")
**Date:** 2026-11-25
**Course lesson:** [Voice AI Foundations, ch. 3: Understanding AgentSession](https://www.livekit-academy.com/courses/voice-ai-foundations/understanding-agent-session)

> Stage 1 — PLAN. Written in the user's own words. No technical design here.

## Problem
When I call the receptionist, I can only **hear** it. I can't see what is going on inside:
is it listening, thinking or speaking? What did it hear me say? Why did the call end?
If something feels slow or wrong, I have nothing to look at.
Also, the speech-to-text may mishear the clinic's name ("bright mile dental").

## What I want (the outcome)
I call the agent on my local server. In a second terminal I run
`docker compose logs -f dental_receptionist` and I can follow the call line by line:

- when the agent changes state (listening → thinking → speaking),
- when I start and stop talking,
- what the agent heard me say (the final text only),
- what the agent answered,
- when the call ended, and why (for example: I hung up).

Before the call, I write down my **prediction** of the state changes. After the call, I compare
it with the logs. And when I say "Bright Smile Dental", the logged text spells it right.

The caller notices no difference. This is only for me, the developer.

## Who uses it
Me, the developer, while testing and fixing the agent. Callers don't see any of it.

## What I want to learn
- The life of an `AgentSession`: created → started → running → closed.
- Events: how to listen with `@session.on(...)`, and what each event object contains.
- Agent states and user states, and the order they come in during one turn.
- That every session already has a VAD (Silero) by default, working with our turn detector.
- Keyterm prompting: helping the speech-to-text hear special words.
- How to test events in code, without making a real call.

## Limits (constraints)
- No new providers, no new keys. Cost: only the tiny test calls we already make.
- Log only what helps: final transcripts, not every partial word. Event handlers must stay quick.
- No web page or UI yet (that comes with the "Agent Frontends" course).
- No saving transcripts to a file or database yet (that comes later, with Postgres).
- English only. Work on `main` (branches are paused).

## My prediction (fill in before the test call)
The state changes I expect for: the agent greets me → I ask "Is Dr. Chen in today?" → the agent answers.

-

## Open questions
- ~~Which special words should we boost?~~ **Decided:** only "Bright Smile Dental". Add more only if the logs show a mistake.
- ~~Should the logs show timing?~~ **Decided:** yes, show how long the agent was "thinking" before it spoke, each turn.
