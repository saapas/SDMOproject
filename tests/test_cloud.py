"""Cloud API tests."""
import pytest

READING = {"device_id": "d1", "gateway_id": "gw-1", "type": "temperature", "value": 21.5, "ts": 100.0}


def test_health(cloud_client):
    assert cloud_client.get("/health").json() == {"status": "ok"}


def test_store_and_list_reading(cloud_client):
    assert cloud_client.post("/readings", json=READING).status_code == 201
    rows = cloud_client.get("/readings").json()
    assert rows == [READING]


def test_gateway_id_defaults_to_unknown(cloud_client):
    r = {k: v for k, v in READING.items() if k != "gateway_id"}
    assert cloud_client.post("/readings", json=r).status_code == 201
    assert cloud_client.get("/readings").json()[0]["gateway_id"] == "unknown"


def test_newest_reading_comes_first(cloud_client):
    for i in range(3):
        cloud_client.post("/readings", json={**READING, "value": float(i), "ts": float(i)})
    values = [r["value"] for r in cloud_client.get("/readings").json()]
    assert values == [2.0, 1.0, 0.0]


def test_limit_parameter(cloud_client):
    for i in range(5):
        cloud_client.post("/readings", json={**READING, "value": float(i)})
    assert len(cloud_client.get("/readings?limit=2").json()) == 2


def test_empty_database_returns_empty_list(cloud_client):
    assert cloud_client.get("/readings").json() == []


@pytest.mark.parametrize("field", ["device_id", "type", "value", "ts"])
def test_missing_required_field_is_422(cloud_client, field):
    r = {k: v for k, v in READING.items() if k != field}
    assert cloud_client.post("/readings", json=r).status_code == 422


def test_non_numeric_value_is_422(cloud_client):
    assert cloud_client.post("/readings", json={**READING, "value": "hot"}).status_code == 422


def test_invalid_limit_is_422(cloud_client):
    assert cloud_client.get("/readings?limit=abc").status_code == 422


def test_sql_injection_in_text_field_is_stored_literally(cloud_client):
    evil = "x'); DROP TABLE readings; --"
    assert cloud_client.post("/readings", json={**READING, "device_id": evil}).status_code == 201
    rows = cloud_client.get("/readings").json()
    assert rows[0]["device_id"] == evil
