# Intent: Run a self-hosted LiveKit server locally in Docker

**Status:** Approved  <!-- Draft → Approved --> (approved by user 2026-11-19)
**Author:** neemydev
**Date:** 2026-11-19
**Course lesson:** [LiveKit Architecture](https://www.livekit-academy.com/courses/livekit-architecture) (Track 0)

> Stage 1 — PLAN. Written in the user's own words. No technical design here.

## Problem
Before building any voice agent, I need a LiveKit server to connect it to.
I don't want to depend on LiveKit Cloud while learning. I want to run the server myself,
on my Mac, inside a Docker container, and understand what it actually does.

## What I want (the outcome)
- I start one command and a LiveKit server runs locally in Docker.
- I can prove it works with a **real audio/video test**: a demo bot streams into a room,
  and I join the same room from my browser and see/hear it.
- After this, our first agent connects to this **local server only** (no LiveKit Cloud for now).

## Who uses it
Me, while learning. Later, all four projects (dental receptionist, restaurant,
healthcare, contact center) connect their agents to this same local server.

## What I want to learn
- What an **SFU** is, and why LiveKit chose it.
- What the **LiveKit server** does, and how LiveKit's architecture fits together
  (rooms, participants, tracks, signaling, WebRTC ports).
- How to run it in a container and why networking is the tricky part.

How I want to learn: explanations in chat as we go, new terms added to `GLOSSARY.md`,
and a diagram of the whole setup.

## Limits (constraints)
- Must run in Docker (all our projects will).
- Local development only — not a production or internet-facing setup.
- No LiveKit Cloud account needed for this step.
- Free: no paid services.

## Open questions
- None from me. Technical choices (ports, config, image version) belong in spec.md.
