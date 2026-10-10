"""Simulated legacy sensor: handshake with the gateway, then send encrypted readings."""
import base64
import json
import os
import random
import time

import requests

from common import kex_legacy as kex

DEVICE_ID = os.getenv("DEVICE_ID", "sensor-001")
SENSOR_TYPE = os.getenv("SENSOR_TYPE", "temperature")
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8080")
INTERVAL = float(os.getenv("INTERVAL", "3"))

b64 = lambda b: base64.b64encode(b).decode()
unb64 = base64.b64decode


def handshake():
    priv, pub = kex.generate_keypair()
    r = requests.post(
        f"{GATEWAY_URL}/handshake",
        json={"device_id": DEVICE_ID, "client_pub": b64(pub)},
        timeout=5,
    )
    r.raise_for_status()
    body = r.json()
    key = kex.derive_session_key(priv, unb64(body["server_pub"]), DEVICE_ID)
    print(f"[{DEVICE_ID}] handshake ok, session={body['session_id']}", flush=True)
    return body["session_id"], key


def read_sensor():
    ranges = {"temperature": (15, 30), "humidity": (30, 80), "pressure": (980, 1040)}
    lo, hi = ranges.get(SENSOR_TYPE, (0, 100))
    # simulated sensor data, not used for cryptography
    return round(random.uniform(lo, hi), 2)  # nosec B311


def main():
    session_id, key = None, None
    while True:
        try:
            if key is None:
                session_id, key = handshake()
            reading = {
                "device_id": DEVICE_ID,
                "type": SENSOR_TYPE,
                "value": read_sensor(),
                "ts": time.time(),
            }
            nonce, ct = kex.encrypt(key, json.dumps(reading).encode(), DEVICE_ID.encode())
            r = requests.post(
                f"{GATEWAY_URL}/telemetry",
                json={"session_id": session_id, "nonce": b64(nonce), "ciphertext": b64(ct)},
                timeout=5,
            )
            if r.status_code in (401, 404):  # session lost / bad key -> redo handshake
                print(f"[{DEVICE_ID}] session rejected ({r.status_code}), re-handshaking", flush=True)
                key = None
                continue
            r.raise_for_status()
            print(f"[{DEVICE_ID}] sent {reading['value']}", flush=True)
        except requests.RequestException as e:
            print(f"[{DEVICE_ID}] network error: {e}", flush=True)
            key = None
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
