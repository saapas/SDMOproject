"""Baseline measurements for the legacy (pre-PQC) system.

Run against a running stack:   python bench/baseline.py
Options (env): GATEWAY_URL, N_HANDSHAKES, N_MESSAGES, N_DEVICES, MSGS_PER_DEVICE
Writes docs/baseline-results.json and docs/baseline-results.md
"""
import base64
import json
import os
import statistics as st
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import kex_legacy as kex  # noqa: E402

GATEWAY = os.getenv("GATEWAY_URL", "http://localhost:8080")
N_HS = int(os.getenv("N_HANDSHAKES", "200"))
N_MSG = int(os.getenv("N_MESSAGES", "500"))
N_DEV = int(os.getenv("N_DEVICES", "20"))
MSGS_PER_DEV = int(os.getenv("MSGS_PER_DEVICE", "25"))

b64 = lambda b: base64.b64encode(b).decode()
unb64 = base64.b64decode
ms = lambda s: s * 1000


def summarize(samples_s):
    xs = sorted(ms(s) for s in samples_s)
    q = lambda p: xs[min(len(xs) - 1, int(p * len(xs)))]
    return {"n": len(xs), "mean_ms": round(st.mean(xs), 3), "p50_ms": round(q(0.5), 3),
            "p95_ms": round(q(0.95), 3), "max_ms": round(xs[-1], 3)}


def do_handshake(sess, device_id):
    priv, pub = kex.generate_keypair()
    body = json.dumps({"device_id": device_id, "client_pub": b64(pub)})
    t0 = time.perf_counter()
    r = sess.post(f"{GATEWAY}/handshake", data=body, headers={"content-type": "application/json"}, timeout=10)
    r.raise_for_status()
    j = r.json()
    key = kex.derive_session_key(priv, unb64(j["server_pub"]), device_id)
    dt = time.perf_counter() - t0
    return j["session_id"], key, dt, len(body), len(r.content), len(pub), len(unb64(j["server_pub"]))


def make_telemetry(key, session_id, device_id):
    reading = {"device_id": device_id, "type": "temperature", "value": 21.5, "ts": time.time()}
    nonce, ct = kex.encrypt(key, json.dumps(reading).encode(), device_id.encode())
    return json.dumps({"session_id": session_id, "nonce": b64(nonce), "ciphertext": b64(ct)})


def send(sess, body):
    t0 = time.perf_counter()
    r = sess.post(f"{GATEWAY}/telemetry", data=body, headers={"content-type": "application/json"}, timeout=10)
    r.raise_for_status()
    return time.perf_counter() - t0


def crypto_only():
    t = time.perf_counter()
    for _ in range(1000):
        kex.generate_keypair()
    keygen = (time.perf_counter() - t) / 1000
    a, apub = kex.generate_keypair()
    b, bpub = kex.generate_keypair()
    t = time.perf_counter()
    for _ in range(1000):
        kex.derive_session_key(a, bpub, "dev")
    derive = (time.perf_counter() - t) / 1000
    return {"keygen_us": round(keygen * 1e6, 1), "derive_us": round(derive * 1e6, 1)}


def device_worker(i):
    sess = requests.Session()
    sid, key, *_ = do_handshake(sess, f"bench-{i:04d}")
    for _ in range(MSGS_PER_DEV):
        send(sess, make_telemetry(key, sid, f"bench-{i:04d}"))


def main():
    sess = requests.Session()
    requests.get(f"{GATEWAY}/health", timeout=5).raise_for_status()

    # 1. handshake time (network + crypto) and sizes
    hs = [do_handshake(sess, "bench-hs") for _ in range(N_HS)]
    handshake = summarize([h[2] for h in hs])
    sizes = {"handshake_request_bytes": hs[0][3], "handshake_response_bytes": hs[0][4],
             "client_pub_raw_bytes": hs[0][5], "server_pub_raw_bytes": hs[0][6]}

    # 2. per-message latency (single device, includes gateway->cloud hop)
    sid, key, *_ = do_handshake(sess, "bench-msg")
    bodies = [make_telemetry(key, sid, "bench-msg") for _ in range(N_MSG)]
    sizes["telemetry_request_bytes"] = len(bodies[0])
    msg = summarize([send(sess, b) for b in bodies])

    # 3. throughput with many concurrent devices
    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=N_DEV) as ex:
        list(ex.map(device_worker, range(N_DEV)))
    wall = time.perf_counter() - t0
    total = N_DEV * MSGS_PER_DEV
    thr = {"devices": N_DEV, "messages": total, "wall_s": round(wall, 2),
           "msgs_per_s": round(total / wall, 1)}

    result = {"suite": kex.SUITE, "handshake": handshake, "message_latency": msg,
              "throughput": thr, "sizes": sizes, "crypto_only": crypto_only()}

    out = Path(__file__).resolve().parent.parent / "docs"
    out.mkdir(exist_ok=True)
    (out / "baseline-results.json").write_text(json.dumps(result, indent=2))
    md = f"""# Baseline results ({kex.SUITE})

Machine / Docker settings: _fill in (CPU, RAM, Docker Desktop backend)_

| Metric | Value |
|---|---|
| Handshake mean / p50 / p95 | {handshake['mean_ms']} / {handshake['p50_ms']} / {handshake['p95_ms']} ms (n={handshake['n']}) |
| Message latency mean / p50 / p95 | {msg['mean_ms']} / {msg['p50_ms']} / {msg['p95_ms']} ms (n={msg['n']}) |
| Throughput | {thr['msgs_per_s']} msg/s ({thr['devices']} devices, {thr['messages']} msgs) |
| Handshake request / response size | {sizes['handshake_request_bytes']} / {sizes['handshake_response_bytes']} bytes |
| Public keys on the wire (raw) | client {sizes['client_pub_raw_bytes']} B, server {sizes['server_pub_raw_bytes']} B |
| Telemetry request size | {sizes['telemetry_request_bytes']} bytes |
| Crypto only: keygen / derive | {result['crypto_only']['keygen_us']} / {result['crypto_only']['derive_us']} us |

Handshake time includes the HTTP round trip plus client-side key generation and derivation.
Message latency includes the gateway -> cloud hop and the SQLite write.
"""
    (out / "baseline-results.md").write_text(md)
    print(md)


if __name__ == "__main__":
    main()
