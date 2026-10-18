import base64
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.core.config import settings
from app.main import create_app


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch, tmp_path) -> Iterator[TestClient]:
    temperature = tmp_path / "temperature"
    temperature.write_text("42000", encoding="ascii")
    monkeypatch.setattr(settings, "ELRS_SERIAL_PORT", None)
    monkeypatch.setattr(settings, "VIDEO_INPUT_DEVICE", None)
    monkeypatch.setattr(settings, "ELRS_ARM_CHANNEL", None)
    monkeypatch.setattr(settings, "API_ACCESS_TOKEN", "test-token")
    monkeypatch.setattr(settings, "HOST_THERMAL_PATH", str(temperature))
    with TestClient(create_app()) as test_client:
        yield test_client


def test_system_health_reports_unconfigured_hardware(client: TestClient) -> None:
    response = client.get("/api/v1/system/health")

    assert response.status_code == 200
    health = response.json()
    assert health["backend_online"] is True
    assert health["elrs_configured"] is False
    assert health["video_input_configured"] is False
    assert health["ready_for_flight"] is False
    assert len(health["checks"]) >= 5
    checks = {check["name"]: check["detail"] for check in health["checks"]}
    assert checks["GPS"] == "GPS satellite telemetry is unavailable."
    assert checks["Battery"] == "Battery telemetry is unavailable."


def test_ai_loadout_is_supplied_by_the_backend(client: TestClient) -> None:
    response = client.get("/api/v1/ai/loadout")

    assert response.status_code == 200
    inventory = response.json()
    assert inventory["mode"] == "missions"
    assert "discovered from model metadata" in inventory["note"]
    assert inventory["router_status"] == "Router weights are missing"
    assert {model["id"] for model in inventory["models"]} == {"human", "vehicle"}
    assert all("weights" in model["status"] for model in inventory["models"])


def test_ai_inference_requires_the_access_token(client: TestClient) -> None:
    response = client.post(
        "/api/v1/ai/infer",
        content=b"image",
        headers={"Content-Type": "image/png"},
    )

    assert response.status_code == 401


def test_ai_inference_rejects_unsupported_media_type(client: TestClient) -> None:
    response = client.post(
        "/api/v1/ai/infer",
        content=b"not an image",
        headers={
            "Authorization": "Bearer test-token",
            "Content-Type": "text/plain",
        },
    )

    assert response.status_code == 415


def test_ai_inference_rejects_oversized_image(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "AI_MAX_IMAGE_BYTES", 4)

    response = client.post(
        "/api/v1/ai/infer",
        content=b"12345",
        headers={
            "Authorization": "Bearer test-token",
            "Content-Type": "image/png",
        },
    )

    assert response.status_code == 413


def test_ai_inference_reports_missing_model_weights(client: TestClient) -> None:
    response = client.post(
        "/api/v1/ai/infer",
        content=b"image",
        headers={
            "Authorization": "Bearer test-token",
            "Content-Type": "image/png",
        },
    )

    assert response.status_code == 503
    assert "router weights are missing" in response.json()["detail"].lower()


def test_vault_items_are_supplied_by_the_backend(client: TestClient) -> None:
    response = client.get("/api/v1/vault/items")

    assert response.status_code == 200
    inventory = response.json()
    assert inventory["mode"] == "demo"
    assert "no media files are stored" in inventory["note"]
    assert {item["media_type"] for item in inventory["items"]} == {
        "image",
        "video",
    }
    assert all(item["captured_at"] is None for item in inventory["items"])


def test_session_cannot_start_without_readiness(client: TestClient) -> None:
    response = client.post(
        "/api/v1/flight/session",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 409
    assert response.json()["detail"]["message"] == (
        "Flight readiness checks have not passed."
    )


def test_control_input_is_range_checked(client: TestClient) -> None:
    response = client.post(
        "/api/v1/flight/control",
        json={"roll": 0, "pitch": 0, "yaw": 0, "throttle": 1.1},
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 422


def test_video_signaling_reports_missing_capture_device(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/video/offer",
        json={"sdp": "v=0\r\n", "type": "offer"},
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "VIDEO_INPUT_DEVICE is not configured"


def test_flight_mutations_require_a_configured_token(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "API_ACCESS_TOKEN", None)

    response = client.post("/api/v1/flight/session")

    assert response.status_code == 503


def test_control_socket_rejects_missing_access_token(client: TestClient) -> None:
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/api/v1/flight/control/ws"):
            pass


def test_control_socket_authenticates_and_checks_flight_state(
    client: TestClient,
) -> None:
    encoded_token = base64.urlsafe_b64encode(b"test-token").decode().rstrip("=")
    with client.websocket_connect(
        "/api/v1/flight/control/ws",
        subprotocols=["aeromind-control", f"aeromind-auth-{encoded_token}"],
    ) as websocket:
        assert websocket.accepted_subprotocol == "aeromind-control"
        websocket.send_json(
            {"roll": 0, "pitch": 0, "yaw": 0, "throttle": 0}
        )
        assert websocket.receive_json() == {
            "error": "An active, armed flight session is required"
        }


def test_control_socket_disconnect_ends_and_disarms_session(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = client.app.state.flight_service
    service._session_active = True
    service._armed = True
    disarm_calls = 0

    async def fake_disarm() -> None:
        nonlocal disarm_calls
        disarm_calls += 1
        service._armed = False

    monkeypatch.setattr(service, "disarm", fake_disarm)
    encoded_token = base64.urlsafe_b64encode(b"test-token").decode().rstrip("=")
    with client.websocket_connect(
        "/api/v1/flight/control/ws",
        subprotocols=["aeromind-control", f"aeromind-auth-{encoded_token}"],
    ):
        pass

    assert disarm_calls == 1
    assert service._armed is False
    assert service._session_active is False


def test_control_heartbeat_timeout_ends_and_disarms_session(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = client.app.state.flight_service
    service._session_active = True
    service._armed = True

    async def fake_disarm() -> None:
        service._armed = False

    monkeypatch.setattr(service, "disarm", fake_disarm)
    encoded_token = base64.urlsafe_b64encode(b"test-token").decode().rstrip("=")
    with pytest.raises(WebSocketDisconnect) as disconnect:
        with client.websocket_connect(
            "/api/v1/flight/control/ws",
            subprotocols=["aeromind-control", f"aeromind-auth-{encoded_token}"],
        ) as websocket:
            websocket.receive_json()

    assert disconnect.value.code == 4408
    assert service._armed is False
    assert service._session_active is False
