# AeroMind

**AeroMind** is a hybrid autonomous drone platform developed by **HackSmiths**.

It is designed to combine real-time manual control, live telemetry, secure multi-user access, and AI-powered identification into a single integrated system. The platform connects a Flutter mobile application, a FastAPI backend, a Raspberry Pi 4 companion computer, and an INAV-based F7 flight controller.

---

## Overview

AeroMind connects the Flutter ground-control app to a FastAPI backend running on the local edge computer. The app and backend communicate over the local network for flight control, telemetry, video, and AI identification.

The system is built with a strong focus on:
- Real-time performance
- Secure access control
- Modular AI support
- Clean separation between flight control and high-level decision making

---

## System Architecture

```text
Flutter Mobile App
        ↕
FastAPI Backend (Raspberry Pi 4)
        ↕  (UART + MSP)
F7 Flight Controller (INAV)
```

No Cloudflare Tunnel is required for local operation. Configure the app with
the edge computer's LAN address, for example
`http://<raspberry-pi-lan-ip>:8100`. Use `http://localhost:8100` only when the
app and backend run on the same machine; on a phone, `localhost` refers to the
phone itself.

## Local setup

On the edge computer, create `aero_cloud/.env` from
`aero_cloud/.env.example`, set a strong `API_ACCESS_TOKEN`, and configure the
flight hardware inputs. Start the local API with `docker compose up --build -d`.
The base Compose setup does not require the video device to be present. When
deploying on the edge computer with its capture device connected at `/dev/video0`,
use the hardware override to pass the device through:

```sh
docker compose -f docker-compose.yml -f docker-compose.hardware.yml up --build -d
```

Compose binds the API on port `8100`; if running
`aero_cloud/main.py` directly, set `HOST=0.0.0.0` so a phone on the same LAN can
reach it. Enter `http://<edge-computer-lan-ip>:8100` and the same access token
in the app's **Link Details**.

This local setup uses plain HTTP on the LAN. Use a trusted private network and
do not expose port `8100` through router port forwarding or a public tunnel.
