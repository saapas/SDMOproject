"""Measurements for the hybrid ML-KEM-768 + X25519 system.

Run against a running stack: ``python bench/mlkem.py``.
The sample counts can be changed with N_HANDSHAKES, N_MESSAGES, N_DEVICES,
and MSGS_PER_DEVICE. Results are written to docs/mlkem-results.json and .md.
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
from common import kex_mlkem as kex  # noqa: E402

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
    return {
        "n": len(xs),
        "mean_ms": round(st.mean(xs), 3),
        "p50_ms": round(q(0.5), 3),
        "p95_ms": round(q(0.95), 3),
        "max_ms": round(xs[-1], 3),
    }


def do_handshake(sess, device_id):
    kem_secret, kem_public, x_private, x_public = kex.generate_keypair()
    body = json.dumps(
        {
            "device_id": device_id,
            "kem_public_key": b64(kem_public),
            "x25519_public_key": b64(x_public),
        }
    )
    t0 = time.perf_counter()
    r = sess.post(
        f"{GATEWAY}/handshake",
        data=body,
        headers={"content-type": "application/json"},
        timeout=10,
    )
    r.raise_for_status()
    response = r.json()
    key = kex.decapsulate(
        kem_secret,
        unb64(response["kem_ciphertext"]),
        x_private,
        unb64(response["server_pub"]),
        device_id,
    )
    dt = time.perf_counter() - t0
    return (
        response["session_id"],
        key,
        dt,
        len(body),
        len(r.content),
        len(kem_public) + len(x_public),
        len(unb64(response["kem_ciphertext"])) + len(unb64(response["server_pub"])),
    )


def make_telemetry(key, session_id, device_id):
    reading = {
        "device_id": device_id,
        "type": "temperature",
        "value": 21.5,
        "ts": time.time(),
    }
    nonce, ciphertext = kex.encrypt(
        key, json.dumps(reading).encode(), device_id.encode()
    )
    return json.dumps(
        {
            "session_id": session_id,
            "nonce": b64(nonce),
            "ciphertext": b64(ciphertext),
        }
    )


def send(sess, body):
    t0 = time.perf_counter()
    r = sess.post(
        f"{GATEWAY}/telemetry",
        data=body,
        headers={"content-type": "application/json"},
        timeout=10,
    )
    r.raise_for_status()
    return time.perf_counter() - t0


def crypto_only():
    t = time.perf_counter()
    for _ in range(100):
        kex.generate_keypair()
    keygen = (time.perf_counter() - t) / 100

    kem_secret, kem_public, x_private, x_public = kex.generate_keypair()
    t = time.perf_counter()
    for _ in range(100):
        key, ciphertext, server_x_public = kex.encapsulate(
            kem_public, x_public, "dev"
        )
        kex.decapsulate(kem_secret, ciphertext, x_private, server_x_public, "dev")
    encapsulate_decapsulate = (time.perf_counter() - t) / 100
    return {
        "keygen_us": round(keygen * 1e6, 1),
        "encapsulate_decapsulate_us": round(encapsulate_decapsulate * 1e6, 1),
    }


def device_worker(i):
    sess = requests.Session()
    sid, key, *_ = do_handshake(sess, f"bench-{i:04d}")
    for _ in range(MSGS_PER_DEV):
        send(sess, make_telemetry(key, sid, f"bench-{i:04d}"))


def main():
    sess = requests.Session()
    requests.get(f"{GATEWAY}/health", timeout=5).raise_for_status()

    handshakes = [do_handshake(sess, "bench-hs") for _ in range(N_HS)]
    handshake = summarize([item[2] for item in handshakes])
    sizes = {
        "handshake_request_bytes": handshakes[0][3],
        "handshake_response_bytes": handshakes[0][4],
        "client_public_material_raw_bytes": handshakes[0][5],
        "server_response_material_raw_bytes": handshakes[0][6],
    }

    sid, key, *_ = do_handshake(sess, "bench-msg")
    bodies = [make_telemetry(key, sid, "bench-msg") for _ in range(N_MSG)]
    sizes["telemetry_request_bytes"] = len(bodies[0])
    message_latency = summarize([send(sess, body) for body in bodies])

    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=N_DEV) as executor:
        list(executor.map(device_worker, range(N_DEV)))
    wall = time.perf_counter() - t0
    total = N_DEV * MSGS_PER_DEV
    throughput = {
        "devices": N_DEV,
        "messages": total,
        "wall_s": round(wall, 2),
        "msgs_per_s": round(total / wall, 1),
    }

    result = {
        "suite": kex.SUITE,
        "handshake": handshake,
        "message_latency": message_latency,
        "throughput": throughput,
        "sizes": sizes,
        "crypto_only": crypto_only(),
    }
    out = Path(__file__).resolve().parent.parent / "docs"
    out.mkdir(exist_ok=True)
    (out / "mlkem-results.json").write_text(json.dumps(result, indent=2))
    md = f"""# ML-KEM benchmark results ({kex.SUITE})

Machine / Docker settings: _fill in (CPU, RAM, Docker Desktop backend)_

| Metric | Value |
|---|---|
| Handshake mean / p50 / p95 | {handshake['mean_ms']} / {handshake['p50_ms']} / {handshake['p95_ms']} ms (n={handshake['n']}) |
| Message latency mean / p50 / p95 | {message_latency['mean_ms']} / {message_latency['p50_ms']} / {message_latency['p95_ms']} ms (n={message_latency['n']}) |
| Throughput | {throughput['msgs_per_s']} msg/s ({throughput['devices']} devices, {throughput['messages']} msgs) |
| Handshake request / response size | {sizes['handshake_request_bytes']} / {sizes['handshake_response_bytes']} bytes |
| Public material on the wire (raw) | client {sizes['client_public_material_raw_bytes']} B, server response {sizes['server_response_material_raw_bytes']} B |
| Telemetry request size | {sizes['telemetry_request_bytes']} bytes |
| Crypto only: keygen / encapsulate+decapsulate | {result['crypto_only']['keygen_us']} / {result['crypto_only']['encapsulate_decapsulate_us']} us |

Handshake time includes the HTTP round trip plus client-side ML-KEM decapsulation
and X25519 derivation. Message latency includes the gateway -> cloud hop and the
SQLite write. Sample counts and settings match the legacy benchmark.
"""
    (out / "mlkem-results.md").write_text(md)
    print(md)


if __name__ == "__main__":
    main()
