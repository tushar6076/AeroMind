from app.schemas.vault import VaultInventory, VaultItem


class VaultService:
    def inventory(self) -> VaultInventory:
        return VaultInventory(
            mode="demo",
            note="Example metadata from the backend; no media files are stored.",
            items=[
                VaultItem(
                    id="demo-image-001",
                    title="Perimeter survey",
                    media_type="image",
                    captured_at=None,
                    duration_seconds=None,
                    size_bytes=None,
                ),
                VaultItem(
                    id="demo-video-001",
                    title="Reconnaissance pass",
                    media_type="video",
                    captured_at=None,
                    duration_seconds=42,
                    size_bytes=None,
                ),
            ],
        )
