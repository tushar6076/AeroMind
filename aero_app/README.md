# AeroMind GCS

The Flutter ground-control app connects to Aero Cloud on the local edge computer.
Configure the backend URL and access token in **Link Details**; the URL can also
be supplied at build time with `AERO_CLOUD_URL` and `AERO_API_TOKEN`.
For a Flutter app running on a phone, use the edge computer's LAN IP, such as
`http://192.168.1.20:8100`; `localhost` on the phone points back to the phone.
Use `http://localhost:8100` only when the app and backend run on the same
machine.

The mobile builds allow cleartext traffic for local HTTP/WebSocket links. Use a
trusted private LAN and do not expose the backend port publicly; the access
token and flight-control traffic are not encrypted by HTTP. For the full
software and edge setup, see the [repository guide](../README.md).

## Service flow

- REST provides health/readiness, flight mode, session, arm, and disarm actions.
- A telemetry WebSocket streams CRSF-derived status to the HUD.
- WebRTC carries video from the backend's UVC capture input to the app.
- An authenticated flight-control WebSocket sends normalized virtual-stick
  input with a heartbeat. Aero Cloud keeps CRSF frames flowing while armed and
  ends/disarms the session when the control heartbeat or connection is lost.

The left stick holds throttle at its last position on release and recenters yaw;
the right stick recenters pitch and roll. Axis/channel direction currently
follows the common Mode 2/AETR convention (CH1 roll, CH2 pitch, CH3 throttle,
CH4 yaw). Confirm the flight-controller channel mapping and failsafe behavior
before enabling arming. Aero Cloud intentionally leaves `ELRS_ARM_CHANNEL`
unset by default.

Run and test the app:

```sh
flutter pub get
flutter analyze
flutter test
flutter run
```

The AI Loadout screen reads its mission inventory from Aero Cloud and can send
a selected JPEG, PNG, or WebP image to the authenticated inference endpoint.
Inference requires trained TorchScript weights installed in the backend model
registry; none are included in Git, so inference reports unavailable until the
weights are deployed. Recon Vault remains a clearly labeled demo catalog and
does not store real media. Stick calibration, failsafe configuration,
persisted missions, and multi-user accounts are not currently exposed by the
backend.
