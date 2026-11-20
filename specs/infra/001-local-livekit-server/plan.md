# Plan: Local LiveKit server in Docker

**Status:** Tested  <!-- Draft → Approved → Built → Tested --> (approved by user 2026-11-20, built 2026-11-20, tested by user 2026-11-20)
**Date:** 2026-11-20
**Project:** infra
**Built from:** spec.md (Approved 2026-11-20)

## Context
Before we can build any voice agent, we need a LiveKit server for it to connect to.
The spec says: one command starts LiveKit in Docker on your Mac, and we prove that real audio and video flow through it.
After you approve, this plan is copied to `specs/infra/001-local-livekit-server/plan.md`.

## Files that change
| File | New or changed | What it does |
|---|---|---|
| `docker-compose.yml` (repo root) | new | Starts the `livekit` container: pinned image, 3 ports, config file, health check |
| `infra/livekit/livekit.yaml` | new | Server settings, with a comment on every line |
| `tests/test_livekit_server.py` | new | Automated tests against the running server |
| `pyproject.toml` / `uv.lock` | changed | Adds `livekit-api` 2.0.1 as a dev tool (`uv add --dev livekit-api`) |
| `.env.example` | changed | Comment lines showing the local values (`ws://localhost:7880`, `devkey`, `secret`). Values stay empty. |
| `README.md` | changed | New "Local LiveKit server" section: start, stop, check, and the media test |
| `CLAUDE.md` | changed | Fills in the "Docker commands" line |

## The settings, and why (what we checked in LiveKit's code and docs)
`livekit.yaml` will contain these settings:
- `port: 7880` is the signaling and API door.
- `bind_addresses: ["0.0.0.0"]` means "listen on every network card *inside the container*".
  - We need this because LiveKit's default is `127.0.0.1`, and then Docker's port mapping can't reach the server.
- `keys: { devkey: secret }` sets the public local key pair.
- `development: true` sets dev mode.
  - Without it, the server logs a scary "secret is too short" error for `secret`.
  - We give our own keys in the file, so dev mode does not change the bind address.
- `rtc.tcp_port: 7881` is the backup media path, over TCP.
- `rtc.udp_port: 7882` is the main media path. All UDP media goes through one port (this is called a "UDP mux").
  - We do not set `port_range_start` / `port_range_end`. The docs say `udp_port` is ignored if those are set.
- `rtc.use_external_ip: false` and `rtc.node_ip: 127.0.0.1` make the server advertise "127.0.0.1" to the browser.
  - The browser sends media to 127.0.0.1, which reaches the mapped ports on your Mac.
- `logging.level: info` keeps logs readable. Dev mode would otherwise switch on very noisy debug logs.

`docker-compose.yml` will contain these settings:
- Image `livekit/livekit-server:v1.13.11`. The version exists for Apple chips (arm64).
- `command: --config /etc/livekit.yaml`.
- The config file is mounted read-only.
- Ports `127.0.0.1:7880:7880`, `127.0.0.1:7881:7881` and `127.0.0.1:7882:7882/udp`.
  - The `127.0.0.1:` part means only your own Mac can connect, not other devices on your Wi-Fi. That matters because the dev keys are public.
- A health check, `wget -q -O- http://127.0.0.1:7880`. The image is Alpine Linux, so it has `wget`.
  - `docker compose ps` then shows `healthy`.

## Order of work
1. Add the test tool: `uv add --dev livekit-api`.
2. Write the tests first (`tests/test_livekit_server.py`) and run them while the server is OFF. They should be **skipped**, with the message "start it with docker compose up -d".
3. Write `infra/livekit/livekit.yaml`, with a comment on every line.
4. Write `docker-compose.yml`.
5. `docker compose up -d`, then `docker compose ps` should show `healthy`, and `curl http://localhost:7880` should print `OK`.
6. Run the tests again. They should now **pass**.
7. **Real media test, done together** (I give you each command):
   - The demo bot joins: `lk room join --url ws://localhost:7880 --api-key devkey --api-secret secret --identity demo-bot --publish-demo my-first-room`
   - Make a token for you: `lk token create --api-key devkey --api-secret secret --join --room my-first-room --identity you --valid-for 24h`
   - Open the example app, enter `ws://localhost:7880` and the token. You should see the bot's video.
   - Open a second tab as `you2`. The two tabs should hear each other.
   - Watch `docker compose logs -f livekit` while you join, to *see* participants and tracks appear.
8. Update `.env.example`, `README.md` and `CLAUDE.md`.
9. Paste the real test output into plan.md and set Status to `Built`. After you've tried it yourself, set it to `Tested`.

## Tests (`tests/test_livekit_server.py`)
- They use `asyncio.run(...)`, so no extra test plugin is needed.
- They connect to `http://localhost:7880` with `devkey` / `secret`.
- These values are fixed in the test. It tests *this* local server, even if `LIVEKIT_URL` later points to the Cloud.
- If the server is not running, the tests are **skipped**, not failed. That way `uv run pytest` still works for the hook tests when Docker is off.

| Test | What it proves |
|---|---|
| `test_server_answers_ok` | The server is up: `GET http://localhost:7880` returns `OK` |
| `test_create_list_delete_room` | It creates room `pytest-room-<random>`, sees it in the list, deletes it, and sees it gone |
| `test_wrong_secret_is_rejected` | A wrong secret is refused. The keys really protect the server. |

## Risks
- **Media may not flow even though the container is "healthy".**
  - Docker on Mac adds a network layer between the browser and the server.
  - So the real media test is the proof, not the green test result.
  - If the media test fails, we read the server logs (the ICE lines) and fix the advertised address.
- **The https example page may refuse `ws://localhost`.**
  - Browsers usually allow `localhost`. If one doesn't, we try another browser, or LiveKit's `meet.livekit.io` custom tab.
- **A port is already in use.** I checked: 7880, 7881 and 7882 are free right now.
- **The tests depend on the server running.** We could miss a failure if the tests silently skip. So the proof below must show **3 passed**, not "skipped".

## Proof (how we know it works)
- Command: `docker compose up -d && uv run pytest -v`
- Expected: the 25 hook tests pass, plus 3 LiveKit tests pass, so 28 passed and 0 skipped.
- Manual check: you see the demo bot's video in the browser, and two tabs hear each other.

## After building (filled in at the end)
Built 2026-11-20.

**Test output** (`docker compose up -d && uv run pytest`):
```text
collected 28 items

tests/test_hooks.py .........................                            [ 89%]
tests/test_livekit_server.py ...                                         [100%]

============================== 28 passed in 2.43s ==============================
livekit-voice-agent-livekit-1  Up About a minute (healthy)
```
With the server OFF, the 3 LiveKit tests showed `3 skipped` ("start it with: docker compose up -d"), as planned.

**Server start-up log** (confirms every setting):
```text
starting LiveKit server {"portHttp": 7880, "nodeIP": "127.0.0.1", "version": "1.13.11",
  "bindAddresses": ["0.0.0.0"], "rtc.portTCP": 7881, "rtc.portUDP": {"Start":7882,"End":0}}
```

**Media check by Claude** (demo bot via `lk room join --publish-demo`):
- The API lists `demo-bot` in `my-first-room` with one `VIDEO video/H264` track, not muted.
- The server log shows the media path it chose: `[local][selected] udp4 host 127.0.0.1:7882`.
  So media flows over the main UDP port, through Docker's port mapping. TCP 7881 was offered as a backup.
- **Browser test by the user (2026-11-20):** joined `my-first-room` at meet.livekit.io (custom tab, `ws://localhost:7880`)
  and saw the demo bot's video, so media flows through our own SFU. Status set to `Tested`.

**What we changed from the plan, and why:**
- The tests ignore one warning, `InsecureKeyLengthWarning` ("secret is shorter than 32 characters").
  It is true and expected for the public local dev keys, so we leave a comment in the test explaining it.
- The README uses `https://meet.livekit.io/?tab=custom` as the browser test page. It has a "custom server" tab where you paste a URL and a token.
