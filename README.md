# AeroMind

AeroMind is a local-network ground-control and edge-computing platform for a
drone. It combines a Flutter ground station, a FastAPI service, Redis-backed
short-lived state, edge AI workspaces, and a documented flight-controller
integration boundary.

## What runs where

```text
Flutter ground-control app
    | REST, telemetry WebSocket, control WebSocket, WebRTC
    v
Aero Cloud on the edge computer (Docker / Python)
    | CRSF transmitter link and flight-controller telemetry
    v
ELRS receiver/transmitter and DYS FC722 running Betaflight

Redis (same local Compose network)
    `-- latest telemetry cache and expiring flight-session metadata

Aero AI workspaces
    `-- model training/export; not yet wired to live Aero Cloud inference
```

The board-specific profile in [`aero_flight/`](aero_flight/README.md) is the
current hardware reference: **DYS FC722 with Betaflight**. Betaflight owns
stabilization, motor mixing, ESC output, and flight-controller failsafes.
AeroMind does not replace that real-time controller. Verify the exact board
revision, target, wiring, receiver/channel mapping, and failsafes against the
physical hardware before connecting or arming. No guessed pin assignments or
flight-ready status should be treated as verified hardware configuration.

## Repository map

| Path | Responsibility | Current state |
| --- | --- | --- |
| [`aero_app/`](aero_app/README.md) | Flutter ground-control UI | Connects to Aero Cloud; hardware-dependent controls remain readiness-gated |
| [`aero_cloud/`](aero_cloud/README.md) | FastAPI edge API, CRSF bridge, video signaling, Redis state | Runnable software service; hardware behavior still needs bench validation |
| [`aero_flight/`](aero_flight/README.md) | Board profile and future companion/controller integration boundaries | Documentation scaffold; no parallel FC firmware implementation |
| [`aero_ai/`](aero_ai/README.md) | Vision and autonomy model workspaces | Training/export workspaces, not live inference services |
| [`docs/IMPLEMENTATION_PLAN.md`](docs/IMPLEMENTATION_PLAN.md) | Current status, dependency-ordered roadmap, and completion gates | Repository-derived; update as work lands |
| [`docker-compose.yml`](docker-compose.yml) | Local API and Redis services | Hardware-independent default |
| [`docker-compose.hardware.yml`](docker-compose.hardware.yml) | Linux edge-device hardware passthrough | Optional override; requires real device paths |

## Quick start: software-only local stack

Prerequisites:

- Git
- Docker Engine and the Docker Compose plugin
- A Flutter SDK compatible with [`aero_app/pubspec.yaml`](aero_app/pubspec.yaml)
  to run the mobile app

On macOS, start your configured Docker engine first (for example, `colima
start`). On a Linux edge computer, ensure Docker is running and the account can
access it.

1. Create the backend environment file if you do not already have one:

   ```sh
   test -f aero_cloud/.env || cp aero_cloud/.env.example aero_cloud/.env
   ```

2. Edit `aero_cloud/.env`:
   - Replace `API_ACCESS_TOKEN` with a long, random private value. Use that same
     value in the app's **Link Details**.
   - Keep `ELRS_SERIAL_PORT` empty until the actual serial device has been
     identified.
   - Keep `ELRS_ARM_CHANNEL` empty until the arm channel has been checked on
     the physical transmitter and Betaflight configuration.
   - Leave `VIDEO_INPUT_DEVICE` empty for a software-only setup.

   The checked-in example is not a secret and must not be used as a production
   token. Never commit `aero_cloud/.env`.

3. Start the API and Redis:

   ```sh
   docker compose up --build -d
   docker compose ps
   curl http://127.0.0.1:8100/
   ```

   The root endpoint is a liveness check. The interactive API docs are at
   `http://127.0.0.1:8100/docs`. Redis is internal to the Compose network; its
   host port is bound to loopback only.

4. Run the Flutter app:

   ```sh
   cd aero_app
   flutter pub get
   flutter analyze
   flutter test
   flutter run
   ```

5. In the app, open **Link Details**, enter `http://<edge-computer-ip>:8100`
   and the same token. On a phone, `localhost` points to the phone, not the
   edge computer. Use a trusted private LAN; the current local HTTP setup does
   not encrypt the access token or control traffic.

Shut down the stack with `docker compose down`. This preserves the Redis volume.
Use `docker compose down -v` only when you intentionally want to delete that
local Redis data.

## Running Aero Cloud without Docker

From the repository root:

```sh
test -f aero_cloud/.env || cp aero_cloud/.env.example aero_cloud/.env
cd aero_cloud
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

This starts the API on the host/port in `.env`. For access from another device,
set `HOST=0.0.0.0` in the local environment file and use the computer's LAN
address in the app. Redis is optional for API startup; without it, the service
logs that short-lived persistence is unavailable and continues with its
in-process state.

## Optional hardware passthrough

Do not use the hardware override on a development machine without the actual
Linux devices. On the edge computer:

1. Identify the video and serial devices from that machine. Do not copy sample
   `/dev` paths without checking them.
2. Set `VIDEO_INPUT_DEVICE=/dev/video0` in `aero_cloud/.env`. This is the
   container path. If the host device has a different path, set the
   Compose-interpolation variable `VIDEO_HOST_DEVICE` in the shell or
   repository-root `.env`; the hardware override maps it to `/dev/video0`
   inside the container.
3. Leave `HOST_THERMAL_PATH` in `aero_cloud/.env` at its container path
   `/sys/class/thermal/thermal_zone0/temp`. Set
   `HOST_THERMAL_HOST_PATH` in the shell or repository-root `.env` only when
   the host's thermal sensor file has a different path. Compose interpolation
   reads shell variables or the repository-root `.env`, not values from
   `aero_cloud/.env`.
4. Set `ELRS_SERIAL_PORT` in `aero_cloud/.env` to the intended container path.
   Edit `docker-compose.hardware.yml` to uncomment and set the serial device
   mapping from the verified host path to that same container path.
5. Verify the `video` and `dialout` groups exist on the Linux host and that the
   container user can access the devices.
6. Only after the FC target, receiver, channel mapping, and failsafes have been
   verified should `ELRS_ARM_CHANNEL` be configured.
7. Start with the override:

   ```sh
   docker compose \
     -f docker-compose.yml \
     -f docker-compose.hardware.yml \
     up --build -d
   ```

Bench-test with propellers removed. A successful API health response is not
proof that the aircraft is safe to arm or fly.

## Current capabilities and limits

- Health/readiness, flight mode, session, arm/disarm, control, and telemetry
  APIs are implemented. Flight actions are authenticated and guarded by
  readiness checks; hardware correctness still needs bench verification.
- Telemetry is delivered over a WebSocket. Control uses an authenticated
  WebSocket with a heartbeat; lost control input or a disconnected client
  causes the in-process flight service to stop the session and attempt to
  disarm.
- WebRTC video signaling is implemented for a configured UVC capture device.
- Redis stores the latest telemetry snapshot with an expiry, publishes
  telemetry updates, and stores expiring session metadata. Only the selected
  mode is restored after restart; an armed or active session is never restored.
- Current control/session authority and live telemetry subscriptions remain
  process-local. The API is intended to run as a **single worker**; Redis
  Pub/Sub is not yet consumed to coordinate multiple API workers.
- Edge AI and Recon Vault endpoints currently provide explicitly marked demo
  catalog data. They do not perform inference or store real media.
- Mission persistence, user accounts, durable flight history, cross-worker
  control coordination, and production TLS are not yet implemented.

See the [Aero Cloud guide](aero_cloud/README.md), the
[Aero Flight scaffold](aero_flight/README.md), and the
[implementation roadmap](docs/IMPLEMENTATION_PLAN.md) before resuming work.

## Validation

Run the checks from the repository root:

```sh
python3 -m pytest -q
cd aero_app
flutter analyze
flutter test
cd ..
docker compose config --quiet
```

Automated tests do not validate a physical aircraft, RF link, video capture
device, or safe failsafe configuration. Complete the hardware gates in the
[implementation roadmap](docs/IMPLEMENTATION_PLAN.md) before any flight test.
