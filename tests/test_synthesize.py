import pytest
from fastapi.testclient import TestClient

from api import routes
from main import app
from simple_voice import UnknownVoice


client = TestClient(app)


def test_simple_passes_controls_without_loading_clone(monkeypatch):
    monkeypatch.setattr(routes, "model_status", lambda: pytest.fail("SIMPLE checked Pocket TTS"))
    received = []
    monkeypatch.setattr(routes, "synthesize_simple", lambda *args: received.append(args) or b"wav")
    response = client.post("/synthesize", json={"voice_type": "SIMPLE", "text": "hello", "voice_name": "Example",
                                               "pitch": 4, "rate": -1, "volume": 80})
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/wav"
    assert received == [("hello", "Example", 4, -1, 80)]


@pytest.mark.parametrize("extra", [{}, {"voice": 0}, {"voice_type": "CLONE"}])
def test_clone_and_older_clients_use_original_backend(monkeypatch, tmp_path, extra):
    path = tmp_path / "sample.wav"
    path.write_bytes(b"clone output")
    monkeypatch.setattr(routes, "model_status", lambda: "ready")
    monkeypatch.setattr(routes, "create_speech", lambda text: str(path))
    response = client.post("/synthesize", json={"text": "hello", **extra})
    assert response.status_code == 200
    assert response.content == b"clone output"
    assert not path.exists()


@pytest.mark.parametrize("overrides", [{"voice_type": "other"}, {"pitch": 11}, {"rate": -11}, {"volume": 101}])
def test_invalid_voice_controls(overrides):
    response = client.post("/synthesize", json={"text": "hello", "voice_type": "SIMPLE", **overrides})
    assert response.status_code == 422


def test_unknown_voice_and_unavailable_clone(monkeypatch):
    def missing(*args):
        raise UnknownVoice("Voice unavailable")

    monkeypatch.setattr(routes, "synthesize_simple", missing)
    monkeypatch.setattr(routes, "model_status", lambda: "failed")
    assert client.post("/synthesize", json={"text": "hello", "voice_type": "SIMPLE"}).status_code == 422
    assert client.post("/synthesize", json={"text": "hello", "voice_type": "CLONE"}).status_code == 503
