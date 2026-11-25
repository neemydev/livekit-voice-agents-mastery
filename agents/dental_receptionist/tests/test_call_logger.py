"""Tests for the call logger: one short "[call] ..." line for each thing that happens in a call.

Spec: specs/dental_receptionist/002-session-events/

Most tests build a real LiveKit event by hand (for example "the agent went from thinking to
speaking") and check the line our code makes from it. No call, no network, no cost.

The last test runs one real text-only turn (it calls OpenAI, tiny cost) with the logger
switched on, and checks the lines really appear. It is skipped when OPENAI_API_KEY is not set.
"""

import logging
import os

import pytest
from dotenv import load_dotenv
from livekit.agents import (
    AgentSession,
    AgentStateChangedEvent,
    CloseEvent,
    ConversationItemAddedEvent,
    UserInputTranscribedEvent,
    UserStateChangedEvent,
)
from livekit.agents.llm import ChatMessage
from livekit.agents.utils import http_context
from livekit.agents.voice.events import CloseReason

# The things we are testing. (This import fails until call_logger.py exists - that is the point.)
from dental_receptionist.call_logger import (
    LOGGER_NAME,
    attach_call_logger,
    describe_agent_state,
    describe_close,
    describe_reply,
    describe_timing,
    describe_transcript,
    describe_user_state,
)

load_dotenv()


# ---------- One event in -> one line out (no network) ----------


def test_agent_state_line() -> None:
    ev = AgentStateChangedEvent(old_state="thinking", new_state="speaking")
    assert describe_agent_state(ev) == "[call] agent: thinking -> speaking"


def test_user_state_line() -> None:
    ev = UserStateChangedEvent(old_state="speaking", new_state="listening")
    assert describe_user_state(ev) == "[call] user: speaking -> listening"


def test_final_transcript_line() -> None:
    ev = UserInputTranscribedEvent(transcript="Is this Bright Smile Dental?", is_final=True)
    assert describe_transcript(ev) == '[call] CALLER said: "Is this Bright Smile Dental?"'


def test_partial_transcript_makes_no_line() -> None:
    # While you talk, STT sends "partial" guesses many times a second. We only log the final text.
    partial = UserInputTranscribedEvent(transcript="Is this Bri", is_final=False)
    empty = UserInputTranscribedEvent(transcript="   ", is_final=True)
    assert describe_transcript(partial) is None
    assert describe_transcript(empty) is None


def test_agent_reply_line() -> None:
    reply = ChatMessage(role="assistant", content=["Yes, this is Bright Smile Dental."])
    ev = ConversationItemAddedEvent(item=reply)
    assert describe_reply(ev) == '[call] AGENT said: "Yes, this is Bright Smile Dental."'


def test_non_message_item_makes_no_line() -> None:
    # The caller's own message is logged from the transcript event, not here (no double lines).
    callers_message = ChatMessage(role="user", content=["Hello"])
    assert describe_reply(ConversationItemAddedEvent(item=callers_message)) is None

    # Not every conversation item is a chat message (we saw a config item in plan mode).
    class SomethingElse:
        role = "assistant"

    assert describe_reply(ConversationItemAddedEvent.model_construct(item=SomethingElse())) is None


def test_timing_line_full() -> None:
    metrics = {"e2e_latency": 0.84, "llm_node_ttft": 0.41, "tts_node_ttfb": 0.22}
    assert describe_timing(metrics) == (
        "[call] timing: replied 0.84 s after you stopped "
        "(llm first word 0.41 s, voice first sound 0.22 s)"
    )


def test_timing_line_partial_and_empty() -> None:
    # In a text-only test (and for the greeting) only some numbers exist. Never crash.
    assert describe_timing({"llm_node_ttft": 1.956}) == "[call] timing: llm first word 1.96 s"
    assert describe_timing({"e2e_latency": 0.9}) == "[call] timing: replied 0.90 s after you stopped"
    assert describe_timing({}) is None


def test_close_line() -> None:
    ev = CloseEvent(reason=CloseReason.PARTICIPANT_DISCONNECTED)
    assert describe_close(ev) == "[call] session closed: participant_disconnected"


# ---------- The logger switched on in a real (text-only) session ----------


@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY is not set - this test needs OpenAI",
)
async def test_logger_in_text_session(caplog: pytest.LogCaptureFixture) -> None:
    from dental_receptionist.agent import Receptionist, build_llm

    # caplog = pytest's "log catcher": it keeps every log line so we can check them.
    caplog.set_level(logging.INFO, logger=LOGGER_NAME)

    async with http_context.open():
        async with build_llm() as llm, AgentSession(llm=llm) as session:
            attach_call_logger(session, room_name="test-room")
            await session.start(Receptionist())
            await session.run(user_input="Hello")
        # Leaving "async with" closes the session -> the "close" event fires.

    lines = [r.getMessage() for r in caplog.records if r.name == LOGGER_NAME]
    print("\n".join(lines))  # shown with "pytest -s", handy to read

    assert "[call] session started in room test-room" in lines
    assert "[call] agent: thinking -> speaking" in lines
    assert any(line.startswith('[call] AGENT said: "') for line in lines)
    assert any(line.startswith("[call] session closed:") for line in lines)
