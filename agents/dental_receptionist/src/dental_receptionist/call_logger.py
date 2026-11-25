"""The call logger: one short "[call] ..." log line for each thing that happens in a call.

Spec: specs/dental_receptionist/002-session-events/
Docs: https://docs.livekit.io/reference/agents/events.md
      https://docs.livekit.io/testing/observability/data.md#per-turn-latency

It has two halves:
  1. "describe_..." functions: take ONE event, return the text of ONE line (or None = "nothing to log").
     They are plain functions, so the tests can check them without a call.
  2. attach_call_logger(): connects those functions to a session's events, and logs the lines.

The caller hears no difference. This is only for us, the developers, to watch a call:
  docker compose logs -f --no-log-prefix dental_receptionist \
    | jq -R -r 'fromjson? | select((.message // "") | startswith("[call]")) | .message'
"""

import logging

from livekit.agents import (
    AgentSession,
    AgentStateChangedEvent,
    CloseEvent,
    ConversationItemAddedEvent,
    UserInputTranscribedEvent,
    UserStateChangedEvent,
)
from livekit.agents.llm import ChatMessage

# Our own named logger. LiveKit sets up logging for the whole program, so our lines go to the
# same place as LiveKit's own logs (the terminal, or "docker compose logs").
LOGGER_NAME = "dental_receptionist.call"
logger = logging.getLogger(LOGGER_NAME)

# Every line starts with this, so our lines are easy to find among LiveKit's.
TAG = "[call]"


# ---------- 1. One event in -> the text of one line out ----------


def describe_agent_state(ev: AgentStateChangedEvent) -> str:
    """The agent changed what it's doing, e.g. thinking -> speaking."""
    return f"{TAG} agent: {ev.old_state} -> {ev.new_state}"


def describe_user_state(ev: UserStateChangedEvent) -> str:
    """The caller started or stopped talking (VAD decides this), or went quiet for a long time ("away")."""
    return f"{TAG} user: {ev.old_state} -> {ev.new_state}"


def describe_transcript(ev: UserInputTranscribedEvent) -> str | None:
    """What the caller said. Only FINAL text: the partial guesses would flood the log."""
    text = ev.transcript.strip()
    if not ev.is_final or not text:
        return None
    return f'{TAG} CALLER said: "{text}"'


def describe_reply(ev: ConversationItemAddedEvent) -> str | None:
    """What the agent said. Only the agent's chat messages: the caller's own words are already
    logged from the transcript, and some items in the history aren't chat messages at all."""
    item = ev.item
    if not isinstance(item, ChatMessage) or item.role != "assistant":
        return None
    return f'{TAG} AGENT said: "{item.text_content}"'


def describe_timing(metrics: dict) -> str | None:
    """How fast the agent answered. LiveKit measures these numbers for every reply
    (ChatMessage.metrics). Some can be missing - e.g. the greeting has no "you stopped talking" -
    so we show only the ones that are there, and nothing at all if none are."""
    parts = []
    if (llm := metrics.get("llm_node_ttft")) is not None:
        parts.append(f"llm first word {llm:.2f} s")
    if (tts := metrics.get("tts_node_ttfb")) is not None:
        parts.append(f"voice first sound {tts:.2f} s")
    details = ", ".join(parts)

    e2e = metrics.get("e2e_latency")
    if e2e is not None:
        text = f"replied {e2e:.2f} s after you stopped"
        if details:
            text += f" ({details})"
    elif details:
        text = details
    else:
        return None
    return f"{TAG} timing: {text}"


def describe_close(ev: CloseEvent) -> str:
    """The session ended, and why (e.g. participant_disconnected = the caller left)."""
    text = f"{TAG} session closed: {ev.reason.value}"
    if ev.error is not None:
        text += f" (error: {ev.error})"
    return text


# ---------- 2. Connect the functions to a session ----------


def attach_call_logger(session: AgentSession, room_name: str) -> None:
    """Switch the call logger on for one session. Call it BEFORE session.start(...),
    so the very first state change ("initializing") is logged too.

    Each handler is a plain (not async) function and must stay QUICK: it runs right when
    the event fires, in the middle of the call. So: build the text, log it, done.
    """

    def log(line: str | None) -> None:
        if line is not None:
            logger.info(line)

    @session.on("agent_state_changed")
    def _on_agent_state(ev: AgentStateChangedEvent) -> None:
        log(describe_agent_state(ev))

    @session.on("user_state_changed")
    def _on_user_state(ev: UserStateChangedEvent) -> None:
        log(describe_user_state(ev))

    @session.on("user_input_transcribed")
    def _on_transcript(ev: UserInputTranscribedEvent) -> None:
        log(describe_transcript(ev))

    @session.on("conversation_item_added")
    def _on_item(ev: ConversationItemAddedEvent) -> None:
        reply = describe_reply(ev)
        log(reply)
        if reply is not None:  # only agent replies carry the timing numbers we want
            log(describe_timing(dict(ev.item.metrics)))

    @session.on("close")
    def _on_close(ev: CloseEvent) -> None:
        log(describe_close(ev))

    log(f"{TAG} session started in room {room_name}")
