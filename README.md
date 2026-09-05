# AeroMind

**AeroMind** is a hybrid autonomous drone platform developed by **HackSmiths**.

It is designed to combine real-time manual control, live telemetry, secure multi-user access, and AI-powered identification into a single integrated system. The platform connects a Flutter mobile application, a FastAPI backend, a Raspberry Pi 4 companion computer, and an INAV-based F7 flight controller.

---

## Overview

AeroMind enables users to control a drone remotely over 4G, monitor live telemetry, switch between map and camera views, and run AI identification models for different applications such as humans, trees, animals, and vehicles.

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
FastAPI Backend (Vercel)
        ↕  (4G - SIM7600)
Raspberry Pi 4
        ↕  (UART + MSP)
F7 Flight Controller (INAV)