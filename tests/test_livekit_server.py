"""Tests for the local LiveKit server running in Docker.

Spec: specs/infra/001-local-livekit-server/

These tests talk to the REAL server, so it must be running:
    docker compose up -d

If the server is not running, every test here is SKIPPED (not failed),
so the other tests in the repo can still run without Docker.
"""

import asyncio
import urllib.request
import uuid

import pytest
from livekit import api

# Fixed values for the LOCAL server only (see infra/livekit/livekit.yaml).
# We do not read LIVEKIT_URL from .env, because later it may point to LiveKit Cloud.
LOCAL_URL = "http://localhost:7880"
LOCAL_API_KEY = "devkey"  # public dev key - local use only
LOCAL_API_SECRET = "secret"  # public dev secret - local use only


def server_is_up() -> bool:
    """True if something answers on port 7880."""
    try:
        with urllib.request.urlopen(LOCAL_URL, timeout=2):
            return True
    except OSError:
        return False


pytestmark = [
    # Skip the whole file when the server is off.
    pytest.mark.skipif(
        not server_is_up(),
        reason="LiveKit server is not running - start it with: docker compose up -d",
    ),
    # The JWT library warns that "secret" is shorter than 32 characters. True, and expected:
    # these are the public LOCAL dev keys. A real server must use a long random secret.
    pytest.mark.filterwarnings("ignore::jwt.warnings.InsecureKeyLengthWarning"),
]


def test_server_answers_ok():
    # The server's front door replies with the plain text "OK".
    with urllib.request.urlopen(LOCAL_URL, timeout=5) as response:
        assert response.status == 200
        assert response.read().decode().strip() == "OK"


def test_create_list_delete_room():
    room_name = f"pytest-room-{uuid.uuid4().hex[:8]}"  # random, so runs never clash

    async def run():
        async with api.LiveKitAPI(
            LOCAL_URL, api_key=LOCAL_API_KEY, api_secret=LOCAL_API_SECRET
        ) as lkapi:
            # 1. Create the room.
            room = await lkapi.room.create_room(api.CreateRoomRequest(name=room_name))
            assert room.name == room_name

            # 2. It shows up in the list of rooms.
            listed = await lkapi.room.list_rooms(api.ListRoomsRequest())
            assert room_name in [r.name for r in listed.rooms]

            # 3. Delete it, and it is gone from the list.
            await lkapi.room.delete_room(api.DeleteRoomRequest(room=room_name))
            listed = await lkapi.room.list_rooms(api.ListRoomsRequest())
            assert room_name not in [r.name for r in listed.rooms]

    asyncio.run(run())


def test_wrong_secret_is_rejected():
    # The API key + secret really protect the server: a wrong secret is refused.
    async def run():
        async with api.LiveKitAPI(
            LOCAL_URL, api_key=LOCAL_API_KEY, api_secret="wrong-secret"
        ) as lkapi:
            with pytest.raises(api.ServerError) as error:
                await lkapi.room.list_rooms(api.ListRoomsRequest())
            assert error.value.status == 401  # 401 = "who are you?" (not authenticated)

    asyncio.run(run())
