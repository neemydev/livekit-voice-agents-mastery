"""Connection test: does the agent in Docker really join rooms on our LOCAL LiveKit server?

Spec: specs/dental_receptionist/001-first-agent/

What it does:
  1. Ask the local server: "send the agent 'dental-receptionist' into room X" (explicit dispatch).
     The room does not exist yet, so the server creates it.
  2. Wait until a participant of kind AGENT shows up in room X.
  3. Delete the room again (this also ends the agent's job).

It needs the Docker stack running:   docker compose up -d
If the server or the agent container is not running, the test is SKIPPED (not failed).
"""

import asyncio
import subprocess
import urllib.request
import uuid

import pytest
from livekit import api

# Fixed values for the LOCAL server only (same as tests/test_livekit_server.py).
LOCAL_URL = "http://localhost:7880"
LOCAL_API_KEY = "devkey"  # public dev key - local use only
LOCAL_API_SECRET = "secret"  # public dev secret - local use only
AGENT_NAME = "dental-receptionist"  # must match @server.rtc_session(agent_name=...)


def server_is_up() -> bool:
    try:
        with urllib.request.urlopen(LOCAL_URL, timeout=2):
            return True
    except OSError:
        return False


def agent_container_is_running() -> bool:
    try:
        out = subprocess.run(
            ["docker", "compose", "ps", "--status", "running", "--services"],
            capture_output=True, text=True, timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return "dental_receptionist" in out.stdout.split()


pytestmark = [
    pytest.mark.skipif(not server_is_up(), reason="LiveKit server is not running - docker compose up -d"),
    pytest.mark.skipif(
        not agent_container_is_running(), reason="agent container is not running - docker compose up -d"
    ),
    # "secret" is a short key: expected for the public LOCAL dev keys.
    pytest.mark.filterwarnings("ignore::jwt.warnings.InsecureKeyLengthWarning"),
]


async def test_agent_joins_new_room() -> None:
    room_name = f"pytest-dental-{uuid.uuid4().hex[:8]}"  # new name, so runs never clash

    async with api.LiveKitAPI(LOCAL_URL, api_key=LOCAL_API_KEY, api_secret=LOCAL_API_SECRET) as lkapi:
        try:
            # 1. Send the agent in (this also creates the room).
            await lkapi.agent_dispatch.create_dispatch(
                api.CreateAgentDispatchRequest(agent_name=AGENT_NAME, room=room_name)
            )

            # 2. Check every half second, for up to 20 seconds, for an AGENT participant.
            agent_joined = False
            for _ in range(40):
                result = await lkapi.room.list_participants(api.ListParticipantsRequest(room=room_name))
                if any(p.kind == api.ParticipantInfo.AGENT for p in result.participants):
                    agent_joined = True
                    break
                await asyncio.sleep(0.5)

            assert agent_joined, f"no agent joined room {room_name} within 20 seconds"
        finally:
            # 3. Clean up: delete the room, which also sends the agent home.
            await lkapi.room.delete_room(api.DeleteRoomRequest(room=room_name))
