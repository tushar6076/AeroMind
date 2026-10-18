# Aero Cloud

Aero Cloud is the FastAPI service used by the AeroMind ground-control app. It is
intended to run on a local edge computer, such as a Raspberry Pi-class Linux
host. It owns the app-facing API, high-level session checks, CRSF control
bridge, telemetry delivery, and WebRTC signaling; Betaflight remains the
real-time flight controller.

## Run locally

From the repository root:

```sh
test -f aero_cloud/.env || cp aero_cloud/.env.example aero_cloud/.env
cd aero_cloud
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

The default `.env.example` binds to `127.0.0.1`, has hardware devices unset, and
leaves the arming channel unset. Replace `API_ACCESS_TOKEN` with a private
random value. To permit a phone on the LAN to connect, set `HOST=0.0.0.0` and
use the computer's LAN IP in the app. Never expose this plain-HTTP service to
the public internet.

Redis is optional for local API startup. To run it with the API in Docker,
follow the [repository setup guide](../README.md). When running the API
directly on the host while Compose runs Redis, the default
`REDIS_URL=redis://localhost:6379/0` is suitable.

## API surfaces

All REST endpoints are under `/api/v1`; OpenAPI docs are at `/docs`.

| Surface | Purpose |
| --- | --- |
| `GET /system/status`, `GET /system/health` | Liveness context and hardware readiness checks |
| `GET /flight/status`, `POST /flight/mode` | Flight status and selected mode |
| `POST/DELETE /flight/session`, `POST /flight/arm`, `POST /flight/disarm` | Guarded session and transmitter operations |
| `POST /flight/control` | Authenticated, range-validated control input |
| `WS /flight/control/ws` | Authenticated control stream with heartbeat/failsafe behavior |
| `WS /telemetry/ws` | Live telemetry snapshots |
| `POST /video/offer` | Authenticated WebRTC offer for configured UVC video |
| `GET /ai/loadout`, `GET /vault/items` | Explicitly marked backend demo catalogs |

Control mutations require the configured `API_ACCESS_TOKEN`. Hardware readiness
does not become true just because the API is responding. See the
[flight-controller integration notes](../aero_flight/README.md) before
connecting hardware.

## Redis responsibilities and limits

`app/services/redis/RedisStore` stores:

- The latest telemetry snapshot under a short TTL (10 seconds by default).
- Expiring flight-session metadata (24 hours by default).
- Telemetry publications on a Redis Pub/Sub channel.

TTL and reconnect settings are in `app/core/config.py`. Startup attempts to
connect but allows the API to continue if Redis is down; writes/reads log
failures and retry after a configured interval. A restart may restore the
selected mode only. It never restores `armed` or `session_active`.

The live flight-control authority, active session, and WebSocket subscriber
queues remain process-local. The service is currently designed for a single
API worker. Although telemetry is published to Redis, no cross-worker Pub/Sub
consumer is wired yet; Redis is not currently a distributed session manager or
a durable event store.

## Tests

From the repository root:

```sh
python3 -m pytest -q aero_cloud/tests
```

The tests cover API/readiness behavior, control-stream failsafes, and Redis
serialization/TTL behavior using an isolated fake client. They do not verify
the real Redis daemon, RF link, camera capture, Betaflight target, or flight
safety.
