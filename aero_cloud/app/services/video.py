import asyncio
import logging

from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer

logger = logging.getLogger(__name__)


class VideoService:
    def __init__(
        self,
        device: str | None,
        width: int,
        height: int,
        frame_rate: int,
    ) -> None:
        self.device = device
        self.width = width
        self.height = height
        self.frame_rate = frame_rate
        self._peers: set[RTCPeerConnection] = set()
        self._player: MediaPlayer | None = None
        self._lock = asyncio.Lock()

    @property
    def configured(self) -> bool:
        return self.device is not None

    @property
    def streaming(self) -> bool:
        return bool(self._peers)

    async def create_answer(
        self,
        offer: RTCSessionDescription,
    ) -> RTCSessionDescription:
        if self.device is None:
            raise RuntimeError("VIDEO_INPUT_DEVICE is not configured")

        async with self._lock:
            if self._player is None:
                self._player = MediaPlayer(
                    self.device,
                    format="v4l2",
                    options={
                        "video_size": f"{self.width}x{self.height}",
                        "framerate": str(self.frame_rate),
                    },
                )
            if self._player.video is None:
                raise RuntimeError(f"No video track found on {self.device}")
            peer = RTCPeerConnection()
            self._peers.add(peer)
            peer.addTrack(self._player.video)

        @peer.on("connectionstatechange")
        async def on_connection_state_change() -> None:
            if peer.connectionState in ("failed", "closed"):
                asyncio.create_task(self.close_peer(peer))

        try:
            await peer.setRemoteDescription(offer)
            answer = await peer.createAnswer()
            await peer.setLocalDescription(answer)
        except (OSError, RuntimeError, ValueError):
            await self.close_peer(peer)
            raise

        assert peer.localDescription is not None
        logger.info("Created WebRTC video peer")
        return peer.localDescription

    async def close_peer(self, peer: RTCPeerConnection) -> None:
        async with self._lock:
            if peer not in self._peers:
                return
            self._peers.remove(peer)
            await peer.close()
            if not self._peers and self._player is not None:
                if self._player.video is not None:
                    self._player.video.stop()
                self._player = None

    async def close(self) -> None:
        for peer in tuple(self._peers):
            await self.close_peer(peer)
