"""Bright Smile Dental receptionist - our first LiveKit voice agent.

Spec: specs/dental_receptionist/001-first-agent/
Shape follows the LiveKit quickstart (https://docs.livekit.io/agents/start/voice-ai.md),
but with PLUGINS (our own Deepgram + OpenAI keys), so it also works on our self-hosted server.

How to run it (from the repo root):
  Talk in the terminal, no server needed:  uv run python -m dental_receptionist.agent console
  In Docker, next to the local server:     docker compose up -d
"""

from dotenv import load_dotenv
from livekit import agents
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    TurnHandlingOptions,
    inference,
)
from livekit.plugins import deepgram, openai

from dental_receptionist.call_logger import attach_call_logger

# Read the API keys from the repo's .env file (if there is one) into the environment.
# Inside Docker there is no .env file; Docker Compose passes the keys in instead.
load_dotenv()

# The system prompt: the rules the LLM reads before EVERY reply.
# Spoken replies must be short and plain - the caller can't scroll back or read symbols.
INSTRUCTIONS = """\
You are the friendly receptionist at Bright Smile Dental, a dental clinic.
You are talking with a caller by voice.

How to speak:
- Keep every reply short: one or two sentences.
- Use plain spoken words. No lists, no emojis, no symbols like asterisks.
- Speak English only.

What you can and cannot do yet:
- You can greet callers, chat politely, and explain what you can't do yet.
- You do NOT have the clinic's opening hours, prices, address, or free appointment times yet.
  Never make these up. Say you don't have that information yet.
- You can NOT book, change or cancel appointments yet. Never say an appointment is booked.
  Say that booking isn't available yet.
"""

# The brain. A small, current OpenAI model. For this model the plugin turns
# "thinking" off by default (reasoning effort "none"), which keeps replies fast.
LLM_MODEL = "gpt-5.4-mini"


def build_llm() -> openai.responses.LLM:
    """Make the LLM. One function, so the agent and the tests always use the same brain."""
    return openai.responses.LLM(model=LLM_MODEL)


# Which Deepgram server to use for the ears (STT) and the mouth (TTS).
# EU, not the default USA server: from our Mac the USA server was slow and unsteady
# (first sound ~1.3 s, voice barely faster than real time -> choppy speech). The EU
# server measured ~0.7 s and 1.5-1.8x real time. Same key, same voices.
# Proof: tests/test_dental_voice_speed.py
DEEPGRAM_HOST = "api.eu.deepgram.com"


# Special words the ears should listen for, so they get spelled right
# ("Bright Smile Dental", not "bright mile dental"). Nova-3 calls this "keyterm"
# (the older "keywords" setting is for Nova-2 only). Spec 002. Proof: tests/test_dental_stt.py
CLINIC_KEYTERMS = ["Bright Smile Dental"]


def build_stt() -> deepgram.STT:
    """The ears: speech -> text."""
    return deepgram.STT(
        model="nova-3",
        language="en",
        keyterm=CLINIC_KEYTERMS,
        base_url=f"https://{DEEPGRAM_HOST}/v1/listen",
    )


def build_tts() -> deepgram.TTS:
    """The mouth: reply -> speech."""
    return deepgram.TTS(model="aura-2-asteria-en", base_url=f"https://{DEEPGRAM_HOST}/v1/speak")


class Receptionist(Agent):
    """WHO the agent is: its instructions. (Later features add tools here.)"""

    def __init__(self) -> None:
        super().__init__(instructions=INSTRUCTIONS)


# The program that waits for calls. It registers with the LiveKit server as an agent.
server = AgentServer()


# "Run this function each time LiveKit sends us a call (a job)."
# agent_name = the name LiveKit uses to send THIS agent into a room (explicit dispatch).
@server.rtc_session(agent_name="dental-receptionist")
async def entrypoint(ctx: JobContext) -> None:
    # One live conversation: plug in the ears, brain and mouth.
    session = AgentSession(
        stt=build_stt(),  # ears: speech -> text
        llm=build_llm(),  # brain: text -> reply
        tts=build_tts(),  # mouth: reply -> speech
        # "Has the caller finished talking?" - the small local model (CPU, free,
        # no LiveKit Cloud keys needed). The default full model would need Cloud.
        turn_handling=TurnHandlingOptions(
            turn_detection=inference.TurnDetector(version="v1-mini"),
        ),
    )

    # Watch the call: log one "[call] ..." line per event (states, what was said, timing,
    # why it ended). Switched on BEFORE start, so we also see the first "initializing" state.
    attach_call_logger(session, room_name=ctx.room.name)

    # Join the room as a participant and start listening (this starts the background jobs).
    await session.start(room=ctx.room, agent=Receptionist())

    # Speak first, like a real receptionist. "await" waits until the greeting is spoken.
    await session.generate_reply(
        instructions="Greet the caller as the receptionist of Bright Smile Dental and ask how you can help."
    )
    # The function ends here, but the call goes on: the session keeps talking in the
    # background until the caller leaves the room.


if __name__ == "__main__":
    # Start the server. The mode comes from the command line: console, dev, start, ...
    agents.cli.run_app(server)
