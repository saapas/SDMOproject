# Legacy edge-cloud baseline (pre-PQC)

device --(X25519 + AES-256-GCM over HTTP)--> gateway --(plain HTTP)--> cloud (SQLite)

Run:  docker compose up --build
Check: curl localhost:8000/readings   |   curl localhost:8080/health

Key exchange code: `common/kex_mlkem.py` implements the default hybrid
ML-KEM-768 + X25519 handshake used by the device and gateway. The legacy
X25519 implementation remains in `common/kex_legacy.py` for migration
compatibility and test comparison.

Known gaps (intentional, for the assignment):
- no tests, no CI/CD, no metrics/structured logs
- no authentication of the gateway -> handshake is vulnerable to active MITM
- no replay protection, sessions never expire, sessions held in memory only
- gateway -> cloud hop is plaintext HTTP
- containers run as root, unpinned dependencies

## Baseline (Part 1)
- Architecture: docs/architecture.md
- Risks: docs/risk-register.md
- Measurements (stack must be running):
    pip install -r bench/requirements.txt
    python bench/baseline.py
  -> writes docs/baseline-results.md / .json. Run it 3 times and keep the median run.

    python bench/mlkem.py
  -> writes docs/mlkem-results.md / .json using the hybrid ML-KEM-768 suite.
     Use the same N_HANDSHAKES, N_MESSAGES, N_DEVICES, and MSGS_PER_DEVICE
     values as the baseline when comparing results.

## Tests (Part 2 of the work plan)
    pip install -r requirements-dev.txt
    python -m pytest --cov=common --cov=gateway --cov=cloud --cov=device --cov-report=term-missing
    python tests/mutation_check.py     # injects 16 defects into a temp copy, checks the tests catch them
