"""Gateway API tests: handshake, telemetry, error handling, cloud failures."""
import pytest
import requests

from common import kex_legacy as kex
from gateway import gateway
from tests.conftest import b64, do_handshake, make_telemetry, unb64


# ---------- health ----------
def test_health(gw):
    r = gw.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_health_reports_session_count(gw):
    do_handshake(gw, "a")
    do_handshake(gw, "b")
    assert gw.get("/health").json()["sessions"] == 2


# ---------- handshake ----------
def test_handshake_returns_session_and_server_key(gw):
    _, pub = kex.generate_keypair()
    r = gw.post("/handshake", json={"device_id": "d1", "client_pub": b64(pub)})
    assert r.status_code == 200
    body = r.json()
    assert len(body["session_id"]) == 32
    assert len(unb64(body["server_pub"])) == 32
    assert body["suite"] == kex.SUITE


def test_handshake_gateway_and_client_agree_on_key(gw):
    sid, key = do_handshake(gw, "d1")
    assert gateway.sessions[sid]["key"] == key
    assert gateway.sessions[sid]["device_id"] == "d1"


def test_each_handshake_creates_an_independent_session(gw):
    s1, k1 = do_handshake(gw, "d1")
    s2, k2 = do_handshake(gw, "d1")
    assert s1 != s2
    assert k1 != k2


@pytest.mark.parametrize("bad_pub", ["not base64 !!", b64(b"short"), b64(b"x" * 33), ""])
def test_handshake_rejects_invalid_public_key(gw, bad_pub):
    r = gw.post("/handshake", json={"device_id": "d1", "client_pub": bad_pub})
    assert r.status_code == 400
    assert len(gateway.sessions) == 0


def test_handshake_rejects_missing_fields(gw):
    assert gw.post("/handshake", json={"device_id": "d1"}).status_code == 422
    assert gw.post("/handshake", json={}).status_code == 422


# ---------- telemetry: happy path ----------
def test_valid_telemetry_is_forwarded_to_cloud(gw, fake_cloud):
    sid, key = do_handshake(gw, "d1")
    reading = {"device_id": "d1", "type": "humidity", "value": 55.5, "ts": 123.0}
    r = gw.post("/telemetry", json=make_telemetry(key, sid, "d1", reading))
    assert r.status_code == 202
    assert len(fake_cloud.calls) == 1
    sent = fake_cloud.calls[0]
    assert sent["url"].endswith("/readings")
    assert sent["json"]["value"] == 55.5
    assert sent["json"]["type"] == "humidity"
    assert sent["json"]["device_id"] == "d1"


def test_gateway_id_is_added_before_forwarding(gw, fake_cloud):
    sid, key = do_handshake(gw, "d1")
    gw.post("/telemetry", json=make_telemetry(key, sid, "d1"))
    assert fake_cloud.calls[0]["json"]["gateway_id"] == gateway.GATEWAY_ID


# ---------- telemetry: rejected input ----------
def test_unknown_session_is_404_and_nothing_forwarded(gw, fake_cloud):
    _, key = do_handshake(gw, "d1")
    r = gw.post("/telemetry", json=make_telemetry(key, "0" * 32, "d1"))
    assert r.status_code == 404
    assert fake_cloud.calls == []


def test_tampered_ciphertext_is_401_and_nothing_forwarded(gw, fake_cloud):
    sid, key = do_handshake(gw, "d1")
    msg = make_telemetry(key, sid, "d1")
    raw = bytearray(unb64(msg["ciphertext"]))
    raw[0] ^= 0x01
    msg["ciphertext"] = b64(bytes(raw))
    r = gw.post("/telemetry", json=msg)
    assert r.status_code == 401
    assert fake_cloud.calls == []


def test_wrong_nonce_is_401(gw, fake_cloud):
    sid, key = do_handshake(gw, "d1")
    msg = make_telemetry(key, sid, "d1")
    msg["nonce"] = b64(bytes(12))
    assert gw.post("/telemetry", json=msg).status_code == 401
    assert fake_cloud.calls == []


def test_message_encrypted_for_other_device_id_is_401(gw, fake_cloud):
    sid, key = do_handshake(gw, "device-A")
    msg = make_telemetry(key, sid, "device-A", aad="device-B")
    assert gw.post("/telemetry", json=msg).status_code == 401
    assert fake_cloud.calls == []


def test_message_from_another_session_key_is_401(gw, fake_cloud):
    sid1, _ = do_handshake(gw, "d1")
    _, key2 = do_handshake(gw, "d1")
    msg = make_telemetry(key2, sid1, "d1")
    assert gw.post("/telemetry", json=msg).status_code == 401
    assert fake_cloud.calls == []


def test_valid_encryption_but_non_json_plaintext_is_401(gw, fake_cloud):
    sid, key = do_handshake(gw, "d1")
    nonce, ct = kex.encrypt(key, b"this is not json", b"d1")
    r = gw.post("/telemetry", json={"session_id": sid, "nonce": b64(nonce), "ciphertext": b64(ct)})
    assert r.status_code == 401
    assert fake_cloud.calls == []


def test_garbage_base64_is_rejected_not_500(gw, fake_cloud):
    sid, _ = do_handshake(gw, "d1")
    r = gw.post("/telemetry", json={"session_id": sid, "nonce": "!!!", "ciphertext": "???"})
    assert r.status_code in (400, 401, 422)


def test_missing_fields_are_422(gw):
    assert gw.post("/telemetry", json={"session_id": "x"}).status_code == 422


# ---------- cloud failures ----------
def test_cloud_connection_error_gives_502(gw, fake_cloud):
    sid, key = do_handshake(gw, "d1")
    fake_cloud.raise_exc = requests.ConnectionError("down")
    assert gw.post("/telemetry", json=make_telemetry(key, sid, "d1")).status_code == 502


def test_cloud_timeout_gives_502(gw, fake_cloud):
    sid, key = do_handshake(gw, "d1")
    fake_cloud.raise_exc = requests.Timeout("slow")
    assert gw.post("/telemetry", json=make_telemetry(key, sid, "d1")).status_code == 502


def test_cloud_500_gives_502(gw, fake_cloud):
    sid, key = do_handshake(gw, "d1")
    fake_cloud.status = 500
    assert gw.post("/telemetry", json=make_telemetry(key, sid, "d1")).status_code == 502


def test_session_survives_a_cloud_failure(gw, fake_cloud):
    sid, key = do_handshake(gw, "d1")
    fake_cloud.status = 500
    gw.post("/telemetry", json=make_telemetry(key, sid, "d1"))
    fake_cloud.status = 201
    assert gw.post("/telemetry", json=make_telemetry(key, sid, "d1")).status_code == 202


# ---------- known gaps (documented in the risk register) ----------
@pytest.mark.xfail(reason="R3: no replay protection in the legacy baseline", strict=False)
def test_replayed_message_is_rejected(gw, fake_cloud):
    sid, key = do_handshake(gw, "d1")
    msg = make_telemetry(key, sid, "d1")
    assert gw.post("/telemetry", json=msg).status_code == 202
    assert gw.post("/telemetry", json=msg).status_code in (401, 409)


@pytest.mark.xfail(reason="R10: session table is unbounded in the legacy baseline", strict=False)
def test_session_table_is_bounded(gw):
    for i in range(1200):
        do_handshake(gw, f"d{i}")
    assert len(gateway.sessions) <= 1000
