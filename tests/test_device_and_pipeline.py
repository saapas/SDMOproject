"""Device behaviour and full device -> gateway -> cloud pipeline tests."""
import pytest

from gateway import gateway


def test_read_sensor_stays_in_range(monkeypatch):
    from device import device as dev
    for sensor, (lo, hi) in {"temperature": (15, 30), "humidity": (30, 80), "pressure": (980, 1040)}.items():
        monkeypatch.setattr(dev, "SENSOR_TYPE", sensor)
        for _ in range(200):
            assert lo <= dev.read_sensor() <= hi


def test_device_handshake_matches_gateway_session(pipeline):
    dev = pipeline["dev"]
    sid, key = dev.handshake()
    assert gateway.sessions[sid]["key"] == key
    assert gateway.sessions[sid]["device_id"] == dev.DEVICE_ID


def test_end_to_end_reading_reaches_cloud_unmodified_and_encrypted_on_the_wire(pipeline, monkeypatch):
    import requests
    dev = pipeline["dev"]
    seen = []
    inner = requests.post

    def spy(url, **kw):
        seen.append((url, kw.get("json")))
        return inner(url, **kw)

    monkeypatch.setattr(requests, "post", spy)
    monkeypatch.setattr(dev.time, "sleep", lambda s: (_ for _ in ()).throw(KeyboardInterrupt))
    monkeypatch.setattr(dev, "read_sensor", lambda: 23.45)
    with pytest.raises(KeyboardInterrupt):
        dev.main()

    rows = pipeline["cloud"].get("/readings").json()
    assert len(rows) == 1
    assert rows[0]["value"] == 23.45
    assert rows[0]["device_id"] == dev.DEVICE_ID
    assert rows[0]["gateway_id"] == gateway.GATEWAY_ID

    telemetry = [j for u, j in seen if u.endswith("/telemetry")]
    assert telemetry and "value" not in telemetry[0]
    assert "23.45" not in str(telemetry[0])


def test_device_rehandshakes_after_gateway_loses_sessions(pipeline, monkeypatch):
    dev = pipeline["dev"]
    calls = {"n": 0}

    def fake_sleep(_):
        calls["n"] += 1
        if calls["n"] == 1:
            gateway.sessions.clear()      # simulate a gateway restart
        else:
            raise KeyboardInterrupt

    monkeypatch.setattr(dev.time, "sleep", fake_sleep)
    with pytest.raises(KeyboardInterrupt):
        dev.main()

    assert len(pipeline["cloud"].get("/readings").json()) == 2
    assert len(gateway.sessions) == 1


def test_device_survives_network_error_and_retries(monkeypatch):
    import requests

    from device import device as dev

    def boom(*a, **k):
        raise requests.ConnectionError("gateway down")

    calls = {"n": 0}

    def fake_sleep(_):
        calls["n"] += 1
        if calls["n"] >= 2:
            raise KeyboardInterrupt

    monkeypatch.setattr(requests, "post", boom)
    monkeypatch.setattr(dev.time, "sleep", fake_sleep)
    with pytest.raises(KeyboardInterrupt):
        dev.main()
    assert calls["n"] == 2


def test_all_outgoing_requests_set_a_timeout(pipeline, monkeypatch):
    import requests
    dev = pipeline["dev"]
    timeouts = []
    inner = requests.post

    def spy(url, **kw):
        timeouts.append(kw.get("timeout"))
        return inner(url, **kw)

    monkeypatch.setattr(requests, "post", spy)
    monkeypatch.setattr(dev.time, "sleep", lambda s: (_ for _ in ()).throw(KeyboardInterrupt))
    with pytest.raises(KeyboardInterrupt):
        dev.main()
    assert len(timeouts) >= 3
    assert all(t is not None and t > 0 for t in timeouts)
