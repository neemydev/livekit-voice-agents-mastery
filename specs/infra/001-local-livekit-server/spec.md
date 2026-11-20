# Spec: Run a self-hosted LiveKit server locally in Docker

**Status:** Approved (approved by user 2026-11-20)
**Date:** 2026-11-19
**Built from:** intent.md (Approved 2026-11-19)

> Stage 2 — DESIGN. What it must do and how it should behave.

## The big picture (diagram)

```text
  YOUR MAC                                              DOCKER CONTAINER
 ┌──────────────────────────────┐                     ┌────────────────────────────┐
 │ Browser tab A (you)          │                     │  LiveKit server (SFU)      │
 │  mic + camera                │── signaling ───────▶│  :7880  WebSocket + API    │
 │                              │   (who, which room) │                            │
 │                              │◀═ media (audio) ═══▶│  :7882  UDP  (main path)   │
 │                              │                     │  :7881  TCP  (backup path) │
 ├──────────────────────────────┤                     │                            │
 │ Demo bot (lk CLI)            │── signaling ───────▶│  Room "my-first-room"      │
 │  streams a demo video        │◀═ media ═══════════▶│   ├ participant: you       │
 └──────────────────────────────┘                     │   └ participant: demo-bot  │
                                                      └────────────────────────────┘
  Ports are "mapped": localhost:7880 on the Mac → port 7880 inside the container, etc.

  The SFU never mixes or re-encodes anything. It receives each track once
  and FORWARDS a copy to every participant who subscribes to it.
```

## Sample session (how it should behave)

> **You:** `docker compose up -d`
> **Terminal:** the `livekit` container starts and keeps running.
> **You:** open `http://localhost:7880` in the browser.
> **Browser:** `OK`
> **You:** start the demo bot in room `my-first-room`, then open LiveKit's example web app
> with a token for the same room, and connect to `ws://localhost:7880`.
> **Browser:** you see the bot's demo video. A second browser tab joins too, and the
> two tabs hear each other. Media really flows through your own SFU.
> **You:** `docker compose down` → everything stops and is cleaned up.

## Must do

- [ ] Start the LiveKit server with **one command**, in Docker, using Docker Compose.
- [ ] Use a **pinned image version** (`livekit/livekit-server:v1.13.11`), not `latest`, so it can't change under us.
- [ ] Keep the server settings in a **config file in the repo**, with a comment on every line explaining it.
- [ ] Use the local dev key pair `devkey` / `secret` (public, well-known, local only).
- [ ] Map the three ports the server needs: `7880` (TCP), `7881` (TCP), `7882` (UDP).
- [ ] Make the server advertise `127.0.0.1` as its address, so the browser on the Mac can reach it.
- [ ] **Real media test:** demo bot + browser in the same room; you see/hear it. Two tabs hear each other.
- [ ] **Automated test** (pytest): the server answers, and we can create, list and delete a room through its API.
- [ ] Add the LiveKit settings for the local server to `.env.example`.
- [ ] A short "how to start / stop / check" section in the README.

## Nice to have

- [ ] A health check, so `docker compose ps` shows `healthy`.
- [ ] Watch the server's logs while you join, to *see* participants and tracks appear.

## Not in this version (out of scope)

- Production setup: HTTPS/TLS, domain name, TURN server, firewall rules.
- Redis / multiple servers (only needed when one server isn't enough).
- Egress (recording), Ingress, SIP (phone calls). They come in later courses.
- Running the agent itself. That is the next spec.

## Parts we will use

| Part          | Choice                                                   | Why                                                                    |
| ------------- | -------------------------------------------------------- | ---------------------------------------------------------------------- |
| Server        | `livekit/livekit-server:v1.13.11` (Docker Hub)         | Official image; newest release (2026-10-25)                            |
| How we run it | Docker Compose (`docker-compose.yml` at the repo root) | One command; later the agents join the same file                       |
| Settings      | `infra/livekit/livekit.yaml`                           | Readable, commented, version-controlled                                |
| Keys          | `devkey` / `secret`                                  | LiveKit's standard local dev pair                                      |
| Media ports   | UDP `7882` (single "mux" port) + TCP `7881` backup   | One UDP port is much easier to map in Docker than 10,000 (50000-60000) |
| Test tools    | `lk` CLI (installed), LiveKit example web app, pytest  | CLI makes tokens + demo bot; web app is a ready-made client            |

## What the docs say

- [Running LiveKit locally](https://docs.livekit.io/transport/self-hosting/local.md): dev mode uses `devkey` / `secret`; the server listens on port `7880`.
- [Ports and firewall](https://docs.livekit.io/transport/self-hosting/ports-firewall.md): `7880` API/WebSocket, `7881` ICE/TCP, `7882` ICE/UDP mux (one port for all UDP), else UDP `50000-60000`.
- [Deployment](https://docs.livekit.io/transport/self-hosting/deployment.md): "If running in a Dockerized environment, host networking should be used for optimal performance."
- [config-sample.yaml](https://github.com/livekit/livekit/blob/master/config-sample.yaml): `rtc.node_ip` sets the address the server advertises; it needs `use_external_ip: false`.
- [Self-hosting overview](https://docs.livekit.io/transport/self-hosting.md): self-hosted = full Agents support, but no built-in inference (bring our own model keys — we have them).
- [LiveKit README](https://github.com/livekit/livekit#readme): `lk token create` makes a join token; `lk room join --publish-demo` streams a demo video; test client at `https://example.livekit.io`.
- Course: [LiveKit Architecture](https://www.livekit-academy.com/courses/livekit-architecture) — WebRTC, P2P vs MCU vs SFU, rooms/participants/tracks, agents as participants.

## Concerns

1. **Docker on Mac + WebRTC networking.** The docs suggest host networking, which works differently
   in Docker Desktop on Mac. Our approach instead: map the 3 ports and advertise `127.0.0.1`. This is
   a common local setup, but we prove it with the real media test, not just "container started".
2. **The next step (agent in Docker) will need care.** If the agent runs in *another* container, `127.0.0.1`
   means "that container itself", so media could fail. Options for the next spec: run the agent on the Mac
   first, or share the server's network. Flagged now, decided in spec 002.
3. **Dev keys are public.** `devkey` / `secret` are fine on your own Mac. Never use them on a server
   reachable from the internet.
4. **Browser test page.** The example app is an `https://` page connecting to `ws://localhost`. Browsers
   normally allow this for `localhost`, but if one refuses, we use another browser or a local test page.
5. **Docs tool.** The `livekit-docs` MCP server wasn't loaded in this chat, so I read the same docs as plain
   Markdown from docs.livekit.io. Same source, just a different way in.
