"""Smoke test for the running stack (used by CI and usable locally).

Checks: cloud and gateway are healthy, at least 3 different sensors have delivered readings
through device -> gateway -> cloud, and the gateway holds at least 3 sessions.
Env: CLOUD_URL (default http://localhost:8000), GATEWAY_URL (default http://localhost:8080), TIMEOUT_S (default 90)
"""
import json
import os
import sys
import time
import urllib.request

CLOUD = os.getenv("CLOUD_URL", "http://localhost:8000")
GATEWAY = os.getenv("GATEWAY_URL", "http://localhost:8080")
TIMEOUT = float(os.getenv("TIMEOUT_S", "90"))


def get(url):
    # URLs come from our own env/defaults and are always http(s) to our own services
    with urllib.request.urlopen(url, timeout=5) as r:  # nosec B310
        return json.loads(r.read())


def wait_for(description, check):
    deadline = time.time() + TIMEOUT
    last = None
    while time.time() < deadline:
        try:
            ok, last = check()
            if ok:
                print(f"OK   {description}: {last}")
                return
        except Exception as e:  # noqa: BLE001 - keep retrying until the deadline
            last = repr(e)
        time.sleep(2)
    print(f"FAIL {description}: last result {last}")
    sys.exit(1)


def main():
    wait_for("cloud /health", lambda: (get(f"{CLOUD}/health").get("status") == "ok", "ok"))
    wait_for("gateway /health", lambda: (get(f"{GATEWAY}/health").get("status") == "ok", "ok"))

    def readings_from_three_sensors():
        devices = {r["device_id"] for r in get(f"{CLOUD}/readings?limit=100")}
        return len(devices) >= 3, sorted(devices)

    wait_for("readings from 3 different sensors in the cloud", readings_from_three_sensors)
    def gateway_sessions():
        n = get(f"{GATEWAY}/health")["sessions"]
        return n >= 3, n

    wait_for("gateway has >= 3 sessions", gateway_sessions)
    print("Smoke test passed")


if __name__ == "__main__":
    main()
