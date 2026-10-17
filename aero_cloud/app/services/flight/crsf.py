import asyncio
import logging
import math
import time
from dataclasses import dataclass

import serial_asyncio

logger = logging.getLogger(__name__)


def _crc8_dvb_s2(data: bytes) -> int:
    crc = 0
    for value in data:
        crc ^= value
        for _ in range(8):
            crc = (
                ((crc << 1) ^ 0xD5) & 0xFF
                if crc & 0x80
                else (crc << 1) & 0xFF
            )
    return crc


def pack_channels(values: list[int]) -> bytes:
    if len(values) != 16 or any(value < 0 or value > 0x7FF for value in values):
        raise ValueError("CRSF channel payload requires 16 unsigned 11-bit values")

    packed = bytearray(22)
    bit_offset = 0
    for value in values:
        for bit in range(11):
            if value & (1 << bit):
                packed[(bit_offset + bit) // 8] |= 1 << ((bit_offset + bit) % 8)
        bit_offset += 11
    return bytes(packed)


def encode_channels(values: list[int]) -> bytes:
    payload = bytes([0x16]) + pack_channels(values)
    return bytes([0xC8, len(payload) + 1]) + payload + bytes(
        [_crc8_dvb_s2(payload)]
    )


@dataclass
class CrsfTelemetry:
    received_at: float = 0
    link_quality: int | None = None
    battery_voltage: float | None = None
    battery_percent: int | None = None
    latitude: float | None = None
    longitude: float | None = None
    satellites: int | None = None
    roll_degrees: float | None = None
    pitch_degrees: float | None = None
    yaw_degrees: float | None = None


class CrsfSerialBridge:
    def __init__(self, port: str, baud_rate: int) -> None:
        self.port = port
        self.baud_rate = baud_rate
        self.telemetry = CrsfTelemetry()
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._reader_task: asyncio.Task[None] | None = None
        self._write_lock = asyncio.Lock()
        self.last_error: str | None = None

    @property
    def connected(self) -> bool:
        return self._writer is not None and not self._writer.is_closing()

    async def connect(self) -> None:
        if self.connected:
            return
        self._reader, self._writer = await serial_asyncio.open_serial_connection(
            url=self.port,
            baudrate=self.baud_rate,
        )
        self.last_error = None
        self._reader_task = asyncio.create_task(self._read_frames())
        logger.info("CRSF serial bridge opened on %s", self.port)

    async def close(self) -> None:
        if self._reader_task is not None:
            self._reader_task.cancel()
            try:
                await self._reader_task
            except asyncio.CancelledError:
                pass
            self._reader_task = None
        if self._writer is not None:
            self._writer.close()
            await self._writer.wait_closed()
            self._writer = None
        self._reader = None

    async def send_controls(
        self,
        *,
        roll: float,
        pitch: float,
        yaw: float,
        throttle: float,
        arm_channel: int,
        arm_value: int,
        disarm_value: int,
        armed: bool,
    ) -> None:
        if not self.connected or self._writer is None:
            raise RuntimeError("ELRS CRSF serial bridge is not connected")
        if not 0 <= throttle <= 1 or any(
            not -1 <= value <= 1 for value in (roll, pitch, yaw)
        ):
            raise ValueError("Control inputs are outside their normalized ranges")
        if not 1 <= arm_channel <= 16:
            raise ValueError("ELRS arm channel must be between 1 and 16")

        def axis(value: float) -> int:
            return round(992 + value * 819)

        channels = [
            axis(roll),
            axis(pitch),
            round(172 + throttle * 1639),
            axis(yaw),
        ]
        channels.extend([992] * 12)
        channels[arm_channel - 1] = arm_value if armed else disarm_value
        async with self._write_lock:
            self._writer.write(encode_channels(channels))
            await self._writer.drain()

    async def _read_frames(self) -> None:
        assert self._reader is not None
        buffer = bytearray()
        try:
            while True:
                chunk = await self._reader.read(256)
                if not chunk:
                    raise OSError("ELRS serial device closed the connection")
                buffer.extend(chunk)
                while len(buffer) >= 4:
                    if buffer[0] not in (0xC8, 0xEA, 0xEC, 0xEE):
                        del buffer[0]
                        continue
                    frame_length = buffer[1]
                    total_length = frame_length + 2
                    if frame_length < 2 or frame_length > 64:
                        del buffer[0]
                        continue
                    if len(buffer) < total_length:
                        break
                    frame = bytes(buffer[:total_length])
                    del buffer[:total_length]
                    if _crc8_dvb_s2(frame[2:-1]) == frame[-1]:
                        self._update_telemetry(frame)
        except asyncio.CancelledError:
            raise
        except OSError as error:
            self.last_error = str(error)
            if self._writer is not None:
                self._writer.close()
            logger.warning("CRSF serial reader stopped: %s", error)

    def _update_telemetry(self, frame: bytes) -> None:
        frame_type = frame[2]
        payload = frame[3:-1]
        self.telemetry.received_at = time.time()
        if frame_type == 0x14 and len(payload) >= 3:
            self.telemetry.link_quality = payload[2]
        elif frame_type == 0x08 and len(payload) >= 8:
            self.telemetry.battery_voltage = int.from_bytes(payload[0:2], "big") / 10
            self.telemetry.battery_percent = payload[7]
        elif frame_type == 0x02 and len(payload) >= 15:
            self.telemetry.latitude = int.from_bytes(
                payload[0:4], "big", signed=True
            ) / 10_000_000
            self.telemetry.longitude = int.from_bytes(
                payload[4:8], "big", signed=True
            ) / 10_000_000
            self.telemetry.satellites = payload[14]
        elif frame_type == 0x1E and len(payload) >= 6:
            self.telemetry.roll_degrees = math.degrees(
                int.from_bytes(payload[0:2], "big", signed=True) / 10_000
            )
            self.telemetry.pitch_degrees = math.degrees(
                int.from_bytes(payload[2:4], "big", signed=True) / 10_000
            )
            self.telemetry.yaw_degrees = math.degrees(
                int.from_bytes(payload[4:6], "big", signed=True) / 10_000
            )
