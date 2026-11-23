# Glossary

Short, simple explanations of the terms, features and ideas used in this project.
Each entry is 2-3 lines. Grouped by topic, A-Z inside each group.

**Contents:** [Voice AI](#voice-ai) · [LiveKit](#livekit) · [Networking & real-time media](#networking--real-time-media) · [Docker](#docker) · [How we work (SDLC)](#how-we-work-sdlc) · [Claude Code](#claude-code) · [Git & GitHub](#git--github) · [Python & tools](#python--tools)

---

## Voice AI

### Echo cancellation
Removing the agent's own voice from the microphone sound. Without it, the agent hears itself
through your speakers and answers itself. Browsers do it for you. In console mode, use headphones.

### Latency budget
The time allowed from "user stops talking" to "agent starts talking": about 0.5 seconds.
Each step (network, STT, LLM, TTS) uses part of it. Network time counts twice: there and back.

### LLM (Large Language Model)
The "brain" of a voice agent. It reads text and writes a reply.
Example: OpenAI's GPT models. In a voice agent it sits between STT and TTS.

### Realtime model (speech-to-speech)
One AI model that hears audio and answers in audio, with no text step in between.
Example: OpenAI Realtime, Gemini Live. Can be faster, but you can't read or change the text in the middle.

### STT (Speech-to-Text)
The "ears" of a voice agent. It turns spoken audio into written text.
Example: you say "book a cleaning", STT gives the text `book a cleaning`. We have Deepgram and Speechmatics.

### System prompt (instructions)
The hidden rules the LLM reads before every reply: who it is and how to behave.
Example: "You are a receptionist at Bright Smile Dental. Keep replies to 1-2 sentences."

### TTS (Text-to-Speech)
The "voice" of a voice agent. It turns the LLM's written reply into spoken audio.
Without TTS the agent could think, but not talk.

### Voice pipeline
The chain a voice agent runs on every turn: **STT → LLM → TTS**.
You speak → it becomes text → the LLM replies in text → the reply is spoken back.

---

## LiveKit

### Access token
A signed "ticket" that lets one participant join one room. It is made with the API key + secret.
Example: `lk token create --join --room my-first-room --identity user1`.

### Agent (class)
Defines WHO the agent is: its `instructions` (system prompt), and later its tools.
Like a job description. Example: `class Receptionist(Agent)` with "You are a friendly receptionist".

### Agent Console
A LiveKit Cloud web page where you click "Start a session" and talk to your agent.
It also shows timing and events for each turn. The course calls it the old name, "Playground".

### Agent dispatch
Sending an agent into a room. We name our agent (`agent_name="dental-receptionist"`) and ask for it by name.
Two ways: inside the token (`lk token create --agent ...`, new rooms only) or with an API call.

### AgentServer
The program that stays running and waits for calls, like a clinic with the lights on.
When a call starts, it runs your `@server.rtc_session` function. One server handles many calls.

### AgentSession
One live conversation. You plug the ears, brain and mouth into it: `stt=`, `llm=`, `tts=`.
Each call gets its own session, so two callers never mix.

### Dev mode keys (`devkey` / `secret`)
LiveKit's standard API key and secret for local testing. Everyone knows them,
so they are only safe on your own computer, never on a server on the internet.

### LiveKit
An open-source platform for real-time audio and video, like the engine behind a video call.
We use it to carry voice between a person and our AI agent with very little delay.

### LiveKit Agents
LiveKit's framework (ready-made code library) for building AI agents that join a call and talk.
It connects STT, LLM and TTS for you, so you focus on what the agent should do.

### LiveKit Cloud
LiveKit's hosted service. They run the servers, so we don't have to.
It gives you three values for `.env`: `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`.

### LiveKit CLI (`lk`)
A command-line tool for LiveKit. You type `lk ...` in the terminal to manage projects, agents and more.
It is already installed on this Mac.

### LiveKit Inference
AI models (STT, LLM, TTS) run for you by LiveKit Cloud. You don't need a separate key per company.
Example: `stt="deepgram/nova-3"` as a plain string. Needs LiveKit Cloud keys.

### LiveKit server
The program at the center of every call: an SFU that routes audio, video and data between participants.
You can use LiveKit Cloud's servers, or run your own ("self-host"), e.g. in Docker.

### node_ip
The address LiveKit tells callers: "send your audio here". Set in `livekit.yaml`; ours is `127.0.0.1`.
That only works for callers who share the same `127.0.0.1`. That's why our agent shares livekit's network.

### Participant
Anything that connects to a room: a person in a browser, a phone caller, or an AI agent.
LiveKit treats them all the same way. An agent is just another participant.

### Plugin (LiveKit)
A small add-on package that connects LiveKit Agents to one AI company, using your own key.
Example: `livekit-agents[deepgram]` lets you write `deepgram.STT()`. The other option is LiveKit Inference.

### Room
A virtual space where a call happens. Participants join a room to talk to each other.
Example: room `my-first-room` with participants `you` and `demo-bot`.

### Run modes
Four ways to start the same agent code: `console` (talk in your terminal, no server),
`dev` (auto-reloads on save), `start` (production), `connect` (join one room to debug).

### Self-hosting
Running software on your own machines instead of using a paid hosted service.
You get full control, but you must set it up, secure it and keep it running.

### Track
One stream of media inside a room, e.g. your microphone audio or your camera video.
Participants *publish* their tracks and *subscribe* to other participants' tracks.

---

## Networking & real-time media

### Bind address
Which network address a server listens on. `127.0.0.1` = "only this machine", `0.0.0.0` = "every address".
Inside a container, LiveKit must listen on `0.0.0.0`, or Docker's port mapping can't reach it.

### Head-of-line blocking
When one lost packet makes everything behind it wait, like a stalled car blocking a whole lane.
TCP (and so WebSocket) does this. It causes short freezes in live voice. UDP doesn't.

### ICE
The process WebRTC uses to find a working network path between two sides.
Each side lists addresses it can be reached on ("candidates"), and they try them until one works.

### ICE candidate
One possible address the media could travel on, e.g. `udp4 127.0.0.1:7882`.
The server log marks the one that won as `[selected]`. In our test that was UDP port 7882.

### localhost (`127.0.0.1`)
Means "this same machine". Each container has its **own** localhost.
So `127.0.0.1` inside the agent container is not the livekit container, unless they share a network.

### MCU (Multipoint Control Unit)
An older way to run group calls: the server decodes everyone's media, mixes it into one stream, and re-encodes it.
Simple for clients, but slow and very heavy for the server.

### P2P (Peer-to-peer)
Every participant sends media directly to every other participant, with no server in between.
Fine for 2 people, but it breaks down quickly: with 5 people, each one uploads 4 copies.

### Port
A numbered "door" on a computer that a program listens on. One computer has many doors.
LiveKit uses 7880 (signaling/API), 7881 (media over TCP), 7882 (media over UDP).

### SFU (Selective Forwarding Unit)
The kind of server LiveKit is. Each participant sends their media **once** to the SFU,
which **forwards** copies to whoever subscribes, without mixing or re-encoding. Fast and scalable.

### Signaling vs media
**Signaling** = the "setup talk": who you are, which room, which tracks exist. WebSocket, port 7880.
**Media** = the actual audio/video. WebRTC, mostly UDP port 7882. Two separate roads, and both must work.

### TCP vs UDP
Two ways to send data. **TCP** re-sends anything lost, so it is reliable but can lag.
**UDP** never waits for lost packets, so it is fast. Live voice prefers UDP: a late sound is useless anyway.

### UDP mux
Sending ALL media through **one** UDP port, instead of a range of 10,000 ports (50000-60000).
Much easier to map in Docker. Ours is port 7882 (`rtc.udp_port` in `livekit.yaml`).

### WebRTC
The standard technology browsers and apps use to send live audio/video with very low delay (~10-30 ms transport).
It mostly uses UDP. LiveKit is built on WebRTC.

### WebSocket
A connection that stays open so both sides can send messages at any time.
LiveKit uses it for signaling (`ws://localhost:7880`), not for the audio itself.

---

## Docker

### Build cache (layers)
Each Dockerfile step makes a saved "layer". If a step and all steps before it didn't change, Docker reuses it.
That's why we install packages BEFORE copying our code: a code change doesn't reinstall everything.

### Build context
The folder Docker can see while building. Ours is the repo root (`context: .`), so it can copy `uv.lock`.
`.dockerignore` hides the rest, e.g. `.env` and tests, so secrets never get into the image.

### Compose override file
A second compose file that changes a few settings of the first one. The later file wins.
Ours: `docker-compose.cloud.yml` swaps the LiveKit URL and keys to Cloud, with no code change.

### Docker
A tool that packs an app and everything it needs into a "container", so it runs the same on any computer.
All four of our projects will run in Docker.

### Docker Compose
A tool to start several containers together from one file, `docker-compose.yml`.
`docker compose up -d` starts everything, `docker compose down` stops it.

### Health check
A small test Docker runs every few seconds to ask a container "are you ready?".
Ours fetches `http://127.0.0.1:7880` and expects `OK`. `docker compose ps` then shows `healthy`.

### Image vs container
An **image** is the packaged app, like a recipe (e.g. `livekit/livekit-server:v1.13.11`).
A **container** is a running copy of that image, like the cooked meal. One image can run as many containers.

### Multi-stage build
A Dockerfile in two parts. The **build** stage has compilers and tools. The **final** stage copies only the finished `.venv`.
The tools are left behind, so the final image is smaller and safer.

### Network namespace
A container's private "network world": its own localhost, its own ports, its own IP address.
Normally each container has its own. `network_mode: "service:livekit"` makes two containers share one.

### Port mapping
Connecting a port on your Mac to a port inside a container, e.g. `7880:7880`.
Without it, the container's doors are closed to the outside, even to your own browser.

### Shared network (`network_mode: "service:..."`)
One container moves into another container's network namespace, like two people living in one house.
Our agent shares livekit's, so `127.0.0.1:7880` reaches the server and the audio address (`node_ip`) works.

---

## How we work (SDLC)

### Feedback loop
One command that proves the work is correct, run after every change. Here: `uv run pytest`.
Claude must show its output before saying "done".

### Gate
A checkpoint where work stops until someone says "yes".
Example: no code is written until you approve `plan.md`.

### intent.md / spec.md / plan.md
The three files we write before any code. **intent** = what and why (your words).
**spec** = how it must behave. **plan** = which files change, in what order, and which tests prove it.

### Open plan
A `plan.md` with status `Approved` or `Built`. Code for a project can only be written while it has an open plan.
`Tested` closes the plan, so new work needs a new plan.

### SDLC (Software Development Life Cycle)
The steps software goes through: plan → design → build → test → deploy → maintain.
We follow Anthropic's "AI-native SDLC playbook", where each step writes a file the next step reads.

### Spec-first development
Write down and agree on *what* to build before writing *code*.
It saves time, because changing a sentence is cheaper than changing code.

---

## Claude Code

### CLAUDE.md
A file of rules and facts that Claude reads at the start of every chat in this project.
Keep it short (under a page). Add a line when Claude repeats a mistake.

### Hook
A small script that Claude Code runs automatically before or after an action, and can block it.
Unlike a request in CLAUDE.md, a hook is *always* enforced. Ours: `protect_env` and `spec_gate`.

### MCP server (Model Context Protocol)
A plug-in that gives Claude extra tools. Our `livekit-docs` MCP server lets Claude search the official LiveKit docs.
This keeps the code up to date instead of relying on Claude's memory.

### Plan mode
A Claude Code mode where Claude can read and think, but cannot change any file.
We use it to make `plan.md`. Claude builds only after you approve the plan.

### Skill
A saved set of instructions Claude loads for a certain kind of task.
Example: `livekit-agents` (how to build LiveKit agents). Unlike a hook, a skill is advice, not a hard rule.

### Slash command
A shortcut you type in the chat that starts a saved task. Ours: `/new-spec`, `/plan`, `/lesson`, `/log-progress`.
They live in `.claude/commands/`.

---

## Git & GitHub

### Commit
A saved snapshot of your files at one moment, with a message saying what changed.
You can always go back to an earlier commit. In this project, you commit, not Claude.

### Force push
Replacing the history on GitHub with your local history (`git push --force-with-lease`).
Only needed after rewriting a commit. Risky on shared repos, so use it rarely.

### Push
Sending your local commits up to GitHub (`git push`).
Until you push, your commits exist only on your Mac.

### Remote
The address of the copy of your repo on GitHub. Ours is called `origin`.
We use `git@github-personal:...` so git uses your personal account, not the work one.

### SSH key
A pair of files that proves to GitHub who you are, without a password.
You have two: one for work, one for personal. The `github-personal` name picks the personal one.

---

## Python & tools

### .env and .env.example
`.env` holds your real secret keys. It is never shared or published.
`.env.example` lists the same key *names* with empty values, so others know which keys they need.

### async / await
`async def` = "this function may pause in the middle". `await` = "pause here until this is done,
and let other work run meanwhile". This lets an agent keep listening while it waits for the LLM.

### Class
A template for making things. `class Receptionist(Agent)` = "a Receptionist is a kind of Agent".
It keeps the agent's instructions and tools together in one box.

### Coroutine
What an `async def` function gives back when you call it. It only runs when something `await`s it.
Forget the `await` and nothing happens, except a warning: "coroutine was never awaited".

### Decorator (`@something`)
A label on the line above a function that gives it a special job.
Example: `@server.rtc_session` means "run this function each time a call starts".

### Flaky test
A test that sometimes passes and sometimes fails with no code change, e.g. because the network is a bit random.
Fix the cause, or measure smarter (like the median). Never just delete the check.

### Inheritance and `super()`
A class can take over all abilities of a parent class, then change only what is different.
`super().__init__(...)` = "parent class, do your normal setup, with these values".

### Median
The middle value after sorting. Tries 0.7 s, 0.8 s, 2.5 s → median **0.8 s**.
One unlucky try doesn't move it, unlike the average (1.33 s). Our voice speed test uses it.

### pytest
Python's most common test tool. It finds files named `test_*.py` and runs the checks inside.
Run it with `uv run pytest`.

### pytest fixture
A setup step pytest runs around a test. Code before `yield` runs first, code after `yield` runs at the end.
Ours opens the web connection pool the plugins need. `autouse=True` = use it for every test in the file.

### Scaffolding
Making a ready-made starter project with the basic files already in place.
Example: `lk agent init my-agent --template agent-starter-python`.

### src layout
Putting a package's code inside a `src/` folder: `agents/dental_receptionist/src/dental_receptionist/`.
The outer folder is the project, the inner one is the Python package. Tests then use the installed code, as Docker does.

### uv
A fast tool that installs Python packages and runs Python code for this project.
`uv add <package>` installs a package, `uv run <file>` runs code with the right packages.

### uv workspace
One repo holding several Python packages that share one `uv.lock`. The root `pyproject.toml` lists them.
Each agent is one package. Docker installs only the one it needs (`uv sync --package dental-receptionist`).
