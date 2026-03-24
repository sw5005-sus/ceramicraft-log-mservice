"""Tests for the health-check HTTP server."""

import urllib.request

import pytest

from ceramicraft_log_mservice.health import start_health_server


@pytest.fixture(scope="module")
def health_port() -> int:
    return 18932  # arbitrary high port unlikely to conflict


@pytest.fixture(scope="module", autouse=True)
def health_server(health_port: int):
    server = start_health_server(port=health_port)
    yield server
    server.shutdown()


def test_ping_returns_ok(health_port: int) -> None:
    """GET /log-ms/v1/ping should return 200 with {"status": "ok"}."""
    url = f"http://127.0.0.1:{health_port}/log-ms/v1/ping"
    with urllib.request.urlopen(url) as resp:
        assert resp.status == 200
        assert resp.read() == b'{"status": "ok"}'


def test_unknown_path_returns_404(health_port: int) -> None:
    """GET on any other path should return 404."""
    url = f"http://127.0.0.1:{health_port}/unknown"
    with pytest.raises(urllib.error.HTTPError) as exc_info:
        urllib.request.urlopen(url)
    assert exc_info.value.code == 404
