# Intent: First dental receptionist agent (greet and chat)

**Status:** Approved  <!-- Draft → Approved --> (approved by user 2026-11-22)
**Author:** neemydev
**Date:** 2026-11-22
**Course lesson:** [Voice AI Foundations, ch. 2: Project setup & your first agent](https://www.livekit-academy.com/courses/voice-ai-foundations/project-setup) (Track 1)

> Stage 1 — PLAN. Written in the user's own words. No technical design here.

## Problem
I understand the boilerplate code from the course (chapter 2) now, but I have no agent of my own yet.
The course scaffolds a project with `lk agent init` and runs it on LiveKit Cloud.
I want to write the first agent myself, in this repo, and run it on **my own LiveKit server**,
because I am learning self-hosting so that we can control it.

## What I want (the outcome)
- I start the agent, join a room on my local LiveKit server, and the
  **Bright Smile Dental** receptionist says hello first.
- I can chat with it by voice. It answers in short, friendly replies (1–2 sentences).
- If I ask about hours or booking, it may guess or say it can't help yet. That is OK for now.
- **Default: the local LiveKit server (Docker).** The same agent can also connect to
  **LiveKit Cloud** by changing settings only, not code. We will build Cloud properly later.

## Who uses it
Me, while learning: I play the patient and talk to it.
Later features grow this into the full receptionist from the course.

## What I want to learn
- **Agent code basics:** AgentServer, `rtc_session`, AgentSession, Agent, async/await —
  written by us and understood line by line.
- **Plugins & providers:** how plugins plug Deepgram and OpenAI into the pipeline, and how keys are loaded.
- **Local vs Cloud switch:** how the same agent connects to my Docker server or to Cloud.
- **Running it in Docker:** the agent in a container, next to the LiveKit server container.

## Limits (constraints)
- **Providers (plugins, my own keys):** ears = Deepgram STT, brain = OpenAI LLM, mouth = Deepgram TTS.
  No LiveKit Inference in this feature.
- Must run in Docker.
- Keep cost tiny: small/cheap models, short test calls.
- English only.
- No booking, no tools, no real clinic data yet.

## Open questions
- How do I talk to it on the local server? (The Agent Console is a Cloud page.) → decide in spec.md.
- What test proves it works? → decide in spec.md.
