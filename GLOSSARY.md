# Glossary

Short, simple explanations of the terms, features and ideas used in this project.
Each entry is 2-3 lines. Grouped by topic, A-Z inside each group.

**Contents:** [Voice AI](#voice-ai) · [LiveKit](#livekit) · [How we work (SDLC)](#how-we-work-sdlc) · [Claude Code](#claude-code) · [Git & GitHub](#git--github) · [Python & tools](#python--tools)

---

## Voice AI

### LLM (Large Language Model)
The "brain" of a voice agent. It reads text and writes a reply.
Example: OpenAI's GPT models. In a voice agent it sits between STT and TTS.

### STT (Speech-to-Text)
The "ears" of a voice agent. It turns spoken audio into written text.
Example: you say "book a cleaning", STT gives the text `book a cleaning`. We have Deepgram and Speechmatics.

### TTS (Text-to-Speech)
The "voice" of a voice agent. It turns the LLM's written reply into spoken audio.
Without TTS the agent could think, but not talk.

### Voice pipeline
The chain a voice agent runs on every turn: **STT → LLM → TTS**.
You speak → it becomes text → the LLM replies in text → the reply is spoken back.

---

## LiveKit

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

### Docker
A tool that packs an app and everything it needs into a "container", so it runs the same on any computer.
All four of our projects will run in Docker.

### pytest
Python's most common test tool. It finds files named `test_*.py` and runs the checks inside.
Run it with `uv run pytest`.

### uv
A fast tool that installs Python packages and runs Python code for this project.
`uv add <package>` installs a package, `uv run <file>` runs code with the right packages.
