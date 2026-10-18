# AeroMind implementation roadmap

**Roadmap basis:** current repository code and documentation, reviewed
2026-10-18. This is a practical engineering roadmap, not a requirements
specification or a claim that hardware has been tested.

## Decisions and boundaries

- The repository's confirmed board reference is the DYS FC722 running
  Betaflight. Betaflight owns the real-time control loop, stabilization, motor
  outputs, and FC failsafes.
- Aero Cloud is the single API-facing companion service. It handles readiness,
  high-level sessions, CRSF control transport, telemetry and video signaling.
- `aero_flight/app/` is documentation-only scaffolding. Do not create a second
  flight controller or duplicate Aero Cloud's CRSF owner without an explicit
  architecture decision.
- The default Compose stack is software-only; physical Linux devices are
  passed through only using the hardware override.
- Flutter contains no demo AI/media inventory. Demo records are clearly marked
  and returned from Aero Cloud.
- Redis currently provides an expiring telemetry cache, telemetry Pub/Sub
  publishing, and expiring session metadata. Live session/control ownership
  remains process-local; the service is single-worker only.

## Current status

| Area | Status | Evidence / limitation |
| --- | --- | --- |
| API and Flutter connection | Implemented | Link Details, health/readiness, flight routes, telemetry/control sockets |
| Backend demo catalogs | Implemented | `/api/v1/ai/loadout` and `/api/v1/vault/items`; not live inference or media |
| Redis short-lived state | Partially implemented | TTL cache and publications exist; no Pub/Sub consumer or cross-worker session ownership |
| Hardware profile | Documented, unverified | DYS FC722 / Betaflight profile; exact revision, target and wiring must be confirmed |
| Video and CRSF hardware | Software path implemented, not bench-verified | Requires real Linux devices and actual receiver/camera setup |
| AI and media production path | Not implemented | Model registry/inference and real media persistence remain future work |
| Production transport/security | Not production-ready | Plain HTTP on trusted LAN only; no production TLS or distributed control |

## Execution phases

### Phase 0 — Reproducible onboarding and repository boundaries

**Status: documented.**

- [x] Document repository modules, software-only startup, edge deployment, and
  test commands in `README.md`.
- [x] Document Aero Cloud responsibilities and Redis limitations in
  `aero_cloud/README.md`.
- [x] Keep generated files and local secrets out of Git; normalize text and
  binary file handling in `.gitignore` and `.gitattributes`.
- [x] Explain the intended, non-executable `aero_flight/app/` structure without
  adding unverified hardware code.
- [x] Keep example arming and video device configuration unset by default.

**Gate:** a new developer can start the API + Redis without hardware, run the
automated checks, and identify which settings are secrets or hardware-specific.

### Phase 1 — Ground-station software contract

**Status: implemented for the current single-process software path.**

- [x] Keep response/request schemas in `aero_cloud/app/schemas/` and app
  transport/model code in `aero_app/lib/core/`.
- [x] Expose system, flight, telemetry, video, AI-catalog and vault routes
  through the versioned API router.
- [x] Enforce access-token checks and input ranges on control mutations.
- [x] Require backend readiness before a real session can start.
- [x] Stop control on heartbeat expiry or control-socket disconnect and attempt
  a disarm.
- [x] Render demo AI and vault records from API responses, with visible demo
  markers.

**Gate:** Python tests, Flutter analysis/tests, and Compose validation pass.
These checks validate software behavior only, not physical safety.

### Phase 2 — Redis-backed state and recovery

**Status: first integration implemented; distributed consistency remains open.**

1. [x] Configure one Redis service for the local Compose network.
2. [x] Cache the latest telemetry with a TTL and publish telemetry updates.
3. [x] Store expiring flight-session metadata and restore only a valid selected
   mode. Never restore an armed or active session.
4. [x] Continue API startup when Redis is unavailable; log failures and
   throttle reconnection attempts.
5. [ ] Add a Pub/Sub subscriber or stream consumer if telemetry must cross API
   worker/process boundaries.
6. [ ] Define ownership, leases, and fencing for control/session state before
   considering more than one API worker.
7. [ ] Decide which records require durable storage; Redis TTL keys are not a
   flight-history database.

**Gate:** real-Redis integration tests prove expiry, recovery, subscriber
behavior and outage handling. Multi-worker deployment remains disabled until
session ownership and safe disconnect/disarm behavior are verified.

### Phase 3 — Verified flight-controller integration

**Status: blocked on hardware/documentation verification; no assumptions should
be filled in from examples.**

1. [ ] Record the exact FC722 board revision, physical MCU marking, and
   Betaflight target from the aircraft.
2. [ ] Obtain and record the authoritative revision-specific pinout and wiring
   diagram in `aero_flight/integration/`.
3. [ ] Verify receiver model/protocol, UART assignment, CRSF port, serial
   settings, and the transmitter's arm channel against the actual Betaflight
   configuration.
4. [ ] Verify channel order, direction, ranges, arming/disarming, failsafe,
   and loss-of-link behavior with propellers removed.
5. [ ] Confirm camera device path, frame format, resolution, frame rate and
   permissions on the target Linux host.
6. [ ] Add or change companion-side adapter code only after ownership and
   protocol contracts are documented. Betaflight remains the real-time
   stabilization and motor-output authority.
7. [ ] Run supervised bench tests with explicit logs before any flight test.

**Gate:** two-person review of wiring/configuration evidence, successful
propeller-off bench tests, verified control loss/disarm behavior, and a written
flight-test checklist. Automated readiness passing alone is not approval to fly.

### Phase 4 — Replace demo AI/media catalogs with real backend capabilities

**Status: not implemented.**

1. [ ] Define versioned model metadata and inference request/result contracts.
2. [ ] Implement an inference adapter with model health, bounded input, timeout,
   and explicit unavailable/error states.
3. [ ] Add tests for model selection, invalid input, inference failure, and
   stale results.
4. [ ] Define media ownership, local storage location, retention, and
   delete/export behavior before storing real captures.
5. [ ] Replace demo endpoints with real inventories only when those services
   exist; keep the UI response-driven and clearly distinguish demo/live state.

**Gate:** end-to-end tests use a controlled model/media fixture and make no
claims of live inference or persisted media when the backing service is absent.

### Phase 5 — Production hardening and operations

**Status: not implemented.**

- [ ] Replace plain HTTP with an authenticated/encrypted transport appropriate
  for the deployment; do not expose the local service publicly.
- [ ] Review CORS, token provisioning/rotation, log redaction, and device
  permissions.
- [ ] Separate liveness from dependency/readiness health and expose Redis
  degradation clearly.
- [ ] Define durable flight records/backups only if product requirements call
  for them; do not use Redis cache keys as an audit log.
- [ ] Add CI to run backend tests, Flutter analysis/tests, and Compose
  validation on supported changes.
- [ ] Document upgrade, recovery, backup/restore, and incident procedures.

**Gate:** documented threat model, operational recovery exercise, dependency
and test checks in CI, and no public exposure of the edge control port.

## Developer verification commands

From the repository root:

```sh
python3 -m pytest -q
cd aero_app
flutter analyze
flutter test
cd ..
docker compose config --quiet
```

For hardware changes, also validate the override on the target Linux edge
computer and complete the propeller-off bench gate above. macOS Compose parsing
cannot establish device availability or permissions.
