"""Speed test: does the agent's voice (TTS) arrive fast enough for live speech?

Bug (2026-11-22): in console mode the voice was choppy ("flush audio emitter due to
slow audio generation"). Measured cause: from this Mac, Deepgram's USA server sends the
voice only just faster than it plays (first sound after ~1.3 s, ~1.2x real time), so any
small network slowdown makes playback run dry. Deepgram's EU server measured ~0.7-1.0 s and
~1.4-1.8x real time.

The rule this test checks, using the agent's OWN mouth (build_tts):
  - the first sound arrives in under 1 second, and
  - voice arrives faster than it plays (more than 1x real time).

The network is a bit random, so one try can be unlucky. We make 3 tries and check the
MIDDLE value (the median): one bad try doesn't fail the test, but a slow server still does.

It calls Deepgram 3 times (tiny cost) and is SKIPPED when DEEPGRAM_API_KEY is not set.
"""

import os
import statistics
import time

import pytest
from dotenv import load_dotenv
from livekit.agents.utils import http_context

load_dotenv()

pytestmark = pytest.mark.skipif(
    not os.getenv("DEEPGRAM_API_KEY"),
    reason="DEEPGRAM_API_KEY is not set - this test needs Deepgram",
)

from dental_receptionist.agent import build_tts  # noqa: E402

GREETING = "Hello, this is Bright Smile Dental. How can I help you today?"
TRIES = 3


async def measure_once() -> tuple[float, float]:
    """Speak the greeting once. Returns (seconds until the first sound, speed vs real time)."""
    tts = build_tts()
    start = time.perf_counter()
    first_sound = None
    audio_seconds = 0.0

    # Stream the text in, like the agent does, and time the audio coming back.
    stream = tts.stream()
    stream.push_text(GREETING)
    stream.end_input()
    async with stream:
        async for chunk in stream:
            if first_sound is None:
                first_sound = time.perf_counter() - start
            audio_seconds += chunk.frame.duration
    wall_seconds = time.perf_counter() - start
    await tts.aclose()
    return first_sound, audio_seconds / wall_seconds


async def test_voice_arrives_fast_enough() -> None:
    async with http_context.open():
        tries = [await measure_once() for _ in range(TRIES)]

    first_sounds = [t[0] for t in tries]
    speeds = [t[1] for t in tries]
    first_sound = statistics.median(first_sounds)
    speed = statistics.median(speeds)
    print(
        "tries: " + ", ".join(f"{f:.2f}s/{s:.1f}x" for f, s in tries)
        + f" -> middle: first sound {first_sound:.2f}s, {speed:.1f}x real time"
    )
    assert first_sound < 1.0, f"first sound took {first_sound:.2f}s in the middle try (limit 1.0s)"
    assert speed > 1.0, f"voice arrives at only {speed:.1f}x real time - playback will stutter"
