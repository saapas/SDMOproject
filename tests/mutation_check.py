"""Poor man's mutation testing: inject known defects and check that the test suite fails.

Usage:  python tests/mutation_check.py
Each mutation is applied to a temporary COPY of the project; your source is never modified.
A mutation is 'caught' when pytest exits with a failure. A surviving mutation means a test gap.
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

TIMEOUT = 40  # seconds per pytest run

# (name, file, old, new)
MUTATIONS = [
    ("Ignore AAD (device binding of ciphertext)", "common/kex_legacy.py", ", aad)", ", None)"),
    ("Reuse a fixed nonce", "common/kex_legacy.py", "nonce = os.urandom(12)", 'nonce = b"\\x00" * 12'),
    ("Drop device ID from key derivation", "common/kex_legacy.py", 'info=f"{SUITE}|{device_id}".encode()', "info=SUITE.encode()"),
    ("Key derived from a constant instead of the ECDH secret", "common/kex_legacy.py", "info=f\"{SUITE}|{device_id}\".encode(),\n    ).derive(shared)", "info=f\"{SUITE}|{device_id}\".encode(),\n    ).derive(b'0' * 32)"),
    ("Gateway: unknown session returns success", "gateway/gateway.py", 'raise HTTPException(404, "unknown session")', 'return {"status": "ignored"}'),
    ("Gateway: cloud failure is swallowed", "gateway/gateway.py", 'raise HTTPException(502, "cloud unreachable")', "pass"),
    ("Gateway: gateway_id not added", "gateway/gateway.py", 'reading["gateway_id"] = GATEWAY_ID', "pass"),
    ("Gateway: cloud HTTP errors ignored", "gateway/gateway.py", ".raise_for_status()\n    except requests.RequestException", "\n    except requests.RequestException"),
    ("Gateway: wrong AAD on decrypt (empty)", "gateway/gateway.py", 's["device_id"].encode()', 'b""'),
    ("Cloud: newest-first ordering removed", "cloud/cloud.py", "ORDER BY id DESC", "ORDER BY id ASC"),
    ("Cloud: limit ignored", "cloud/cloud.py", "(min(limit, 1000),)", "(1000,)"),
    ("Device: never re-handshakes on 401/404", "device/device.py", "if r.status_code in (401, 404):", "if False:"),
    ("Handshake: client key length check removed", "gateway/gateway.py", "if len(client_pub) != 32:", "if False:"),
    ("Handshake: static server keypair for all sessions", "gateway/gateway.py", "priv, pub = kex.generate_keypair()", 'priv, pub = globals().setdefault("_S", kex.generate_keypair())'),
    ("Gateway: no timeout on the cloud call", "gateway/gateway.py", "json=reading, timeout=5)", "json=reading)"),
    ("Device: no timeouts on requests", "device/device.py", "timeout=5,", ""),
]


def run_tests(cwd):
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    try:
        p = subprocess.run([sys.executable, "-m", "pytest", "-x", "-q", "-p", "no:cacheprovider"],
                           cwd=cwd, env=env, capture_output=True, text=True, timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        return 99  # a hang counts as detected (the suite did not pass)
    return p.returncode


def main():
    ignore = shutil.ignore_patterns("__pycache__", ".git", "data", ".pytest_cache", ".venv")
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp) / "baseline"
        shutil.copytree(ROOT, base, ignore=ignore)
        if run_tests(base) != 0:
            print("Unmodified code fails its own tests; fix that first.")
            sys.exit(2)

        results = []
        for i, (name, rel, old, new) in enumerate(MUTATIONS):
            work = Path(tmp) / f"m{i}"
            shutil.copytree(ROOT, work, ignore=ignore)
            f = work / rel
            text = f.read_text()
            if old not in text:
                results.append((name, "SKIPPED (pattern not found)"))
                continue
            f.write_text(text.replace(old, new))
            results.append((name, "caught" if run_tests(work) != 0 else "SURVIVED"))

    width = max(len(n) for n, _ in results)
    print(f"{'Injected defect'.ljust(width)}  Result")
    print("-" * (width + 12))
    for n, r in results:
        print(f"{n.ljust(width)}  {r}")
    caught = sum(r == "caught" for _, r in results)
    print(f"\n{caught}/{len(results)} injected defects caught")


if __name__ == "__main__":
    main()
