"""Shared fixtures. DB_PATH must be set before the cloud module is imported."""
import base64
import json
import os
import tempfile
import time

import pytest
import requests
from fastapi.testclient import TestClient

os.environ["DB_PATH"] = os.path.join(tempfile.mkdtemp(), "readings.db")

from cloud import cloud  # noqa: E402
from common import kex_legacy as kex  # noqa: E402
from gateway import gateway  # noqa: E402

b64 = lambda b: base64.b64encode(b).decode()
unb64 = base64.b64decode

GW_BASE = "http://gw.test"
CLOUD_BASE = "http://cloud.test"


class FakeResponse:
    def __init__(self, status_code=201):
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"status {self.status_code}")


@pytest.fixture
def gw():
    gateway.sessions.clear()
    return TestClient(gateway.app)


@pytest.fixture
def cloud_client():
    conn = cloud.db()
    with conn:
        conn.execute("DELETE FROM readings")
    conn.close()
    return TestClient(cloud.app)


@pytest.fixture
def fake_cloud(monkeypatch):
    """Replace the gateway's HTTP call to the cloud with a recorder."""
    class Recorder:
        calls = []
        status = 201
        raise_exc = None

    rec = Recorder()
    rec.calls = []

    def fake_post(url, json=None, timeout=None, **kw):
        rec.calls.append({"url": url, "json": json})
        if rec.raise_exc:
            raise rec.raise_exc
        return FakeResponse(rec.status)

    monkeypatch.setattr(gateway.requests, "post", fake_post)
    return rec


@pytest.fixture
def pipeline(monkeypatch, gw, cloud_client):
    """Route requests.post to the in-process gateway and cloud apps (device -> gateway -> cloud)."""
    from device import device as dev

    def router(url, **kw):
        if url.startswith(GW_BASE):
            return gw.post(url[len(GW_BASE):], **kw)
        if url.startswith(CLOUD_BASE):
            return cloud_client.post(url[len(CLOUD_BASE):], **kw)
        raise AssertionError(f"unexpected url {url}")

    monkeypatch.setattr(requests, "post", router)
    monkeypatch.setattr(dev, "GATEWAY_URL", GW_BASE)
    monkeypatch.setattr(gateway, "CLOUD_URL", CLOUD_BASE)
    return {"gw": gw, "cloud": cloud_client, "dev": dev}


# ---- helpers used by several test modules ----
def do_handshake(client, device_id="sensor-001"):
    """Perform a client-side handshake. Returns (session_id, key)."""
    priv, pub = kex.generate_keypair()
    r = client.post("/handshake", json={"device_id": device_id, "client_pub": b64(pub)})
    assert r.status_code == 200, r.text
    body = r.json()
    key = kex.derive_session_key(priv, unb64(body["server_pub"]), device_id)
    return body["session_id"], key


def make_telemetry(key, session_id, device_id="sensor-001", reading=None, aad=None):
    reading = reading or {"device_id": device_id, "type": "temperature", "value": 21.5, "ts": time.time()}
    nonce, ct = kex.encrypt(key, json.dumps(reading).encode(), (aad or device_id).encode())
    return {"session_id": session_id, "nonce": b64(nonce), "ciphertext": b64(ct)}
