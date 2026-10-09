# Legacy edge-cloud baseline (pre-PQC)

device --(X25519 + AES-256-GCM over HTTP)--> gateway --(plain HTTP)--> cloud (SQLite)

Run:  docker compose up --build
Check: curl localhost:8000/readings   |   curl localhost:8080/health

Key code to replace with ML-KEM: common/kex_legacy.py (+ /handshake in gateway, handshake() in device).

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
- Tag it:  git tag baseline-legacy

## Tests (Part 2 of the work plan)
    pip install -r requirements-dev.txt
    python -m pytest --cov=common --cov=gateway --cov=cloud --cov=device --cov-report=term-missing
    python tests/mutation_check.py     # injects 12 defects into a temp copy, checks the tests catch them

- 56 tests + 2 expected failures (xfail = known gaps R3 replay and R10 unbounded sessions; remove the marker when fixed)
- Everything runs in-process (no Docker needed); the pipeline test wires device -> gateway -> cloud together
