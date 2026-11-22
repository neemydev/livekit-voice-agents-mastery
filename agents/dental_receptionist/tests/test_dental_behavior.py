"""Behavior tests for the Bright Smile Dental receptionist.

Spec: specs/dental_receptionist/001-first-agent/

How they work (LiveKit's testing tools, https://docs.livekit.io/testing/unit-tests.md):
  1. Start an AgentSession with only a brain (LLM): no microphone, no speaker, no LiveKit server.
  2. session.run(user_input="...") plays ONE turn: the "caller" types a line, the agent answers.
  3. .judge(llm, intent="...") asks an LLM: "does this answer match the intent?"

They call OpenAI, so each run costs a tiny amount.
They are SKIPPED (not failed) when OPENAI_API_KEY is not set.
"""

import os

import pytest
from dotenv import load_dotenv
from livekit.agents import AgentSession
from livekit.agents.utils import http_context

# Read the keys from the repo's .env file (python-dotenv walks up the folders to find it).
load_dotenv()

pytestmark = pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY is not set - these tests need OpenAI",
)

# The things we are testing. (This import fails until agent.py exists - that is the point.)
from dental_receptionist.agent import Receptionist, build_llm  # noqa: E402


@pytest.fixture(autouse=True)
async def livekit_http_session():
    """Before each test: open the web connection pool that plugins use.

    In a real call, LiveKit opens it for us (the "job context"). A test has no call,
    so we open it here. Without it, the OpenAI plugin fails with
    "Attempted to use an http session outside of a job context".
    """
    async with http_context.open():
        yield


async def test_greets_as_bright_smile() -> None:
    # "async with" opens the LLM and the session, and closes them again at the end.
    async with build_llm() as llm, AgentSession(llm=llm) as session:
        await session.start(Receptionist())

        result = await session.run(user_input="Hello")

        # The first thing that happens is the agent answering with a message...
        await result.expect.next_event().is_message(role="assistant").judge(
            llm,
            intent=(
                "A short (one or two sentences), friendly greeting from the receptionist "
                "of a dental clinic called Bright Smile Dental, offering to help."
            ),
        )
        # ...and nothing else happens in this turn (no tool calls, no second message).
        result.expect.no_more_events()


async def test_does_not_invent_hours() -> None:
    async with build_llm() as llm, AgentSession(llm=llm) as session:
        await session.start(Receptionist())

        result = await session.run(user_input="What time do you open tomorrow?")

        await result.expect.next_event().is_message(role="assistant").judge(
            llm,
            intent=(
                "Does NOT give any specific opening hours, days or times. "
                "Says, politely, that it doesn't have that information yet."
            ),
        )


async def test_does_not_book() -> None:
    async with build_llm() as llm, AgentSession(llm=llm) as session:
        await session.start(Receptionist())

        result = await session.run(user_input="I'd like to book a cleaning for next Monday.")

        await result.expect.next_event().is_message(role="assistant").judge(
            llm,
            intent=(
                "Says it cannot book appointments yet. Does NOT claim that an appointment "
                "was booked, reserved or scheduled, and does NOT suggest any new date or time "
                "of its own. Repeating the day the caller asked for is fine."
            ),
        )
