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

### Run the benchmarks

Both benchmark scripts require the cloud and gateway services to be running
on `localhost:8000` and `localhost:8080`.

#### Option 1: Docker Compose

From the repository root, build and start the stack:

```powershell
docker compose up --build -d
```

Check that the services are ready:

```powershell
Invoke-WebRequest http://localhost:8080/health
Invoke-WebRequest http://localhost:8000/health
```

Install the benchmark dependencies in the Python environment used to run the
scripts:

```powershell
python -m pip install -r bench/requirements.txt
```

Run the legacy and ML-KEM benchmarks with the same settings:

```powershell
$env:N_HANDSHAKES="200"
$env:N_MESSAGES="500"
$env:N_DEVICES="20"
$env:MSGS_PER_DEVICE="25"

python bench/baseline.py
python bench/mlkem.py
```

Stop the stack when finished:

```powershell
docker compose down
```

#### Option 2: Run the services locally

If Docker Desktop is unavailable, install the service dependencies:

```powershell
python -m pip install -r gateway/requirements.txt
python -m pip install -r cloud/requirements.txt
python -m pip install -r bench/requirements.txt
```

Open two PowerShell terminals from the repository root. Start the cloud in
the first terminal:

```powershell
$env:DB_PATH="$PWD\.tmp-benchmark-readings.db"
python -m uvicorn cloud.cloud:app --host 127.0.0.1 --port 8000
```

Start the gateway in the second terminal:

```powershell
$env:CLOUD_URL="http://127.0.0.1:8000"
python -m uvicorn gateway.gateway:app --host 127.0.0.1 --port 8080
```

In a third terminal, verify the gateway and run the benchmarks:

```powershell
Invoke-WebRequest http://127.0.0.1:8080/health
$env:GATEWAY_URL="http://127.0.0.1:8080"
$env:N_HANDSHAKES="200"
$env:N_MESSAGES="500"
$env:N_DEVICES="20"
$env:MSGS_PER_DEVICE="25"

python bench/baseline.py
python bench/mlkem.py
```

The ML-KEM benchmark measures the hybrid ML-KEM-768 + X25519 handshake,
steady-state AES-GCM telemetry latency, throughput, request sizes, and
crypto-only session-key establishment. It writes:

- `docs/mlkem-results.md` — human-readable results table
- `docs/mlkem-results.json` — raw measurements

The legacy benchmark writes the corresponding files:

- `docs/baseline-results.md`
- `docs/baseline-results.json`

For a fair comparison, run both scripts back-to-back in the same environment
with the same values for `N_HANDSHAKES`, `N_MESSAGES`, `N_DEVICES`, and
`MSGS_PER_DEVICE`. The report-ready comparison is in
`docs/project-report.md`. Run each benchmark multiple times and compare
medians when making performance claims.

## Tests (Part 2 of the work plan)
    pip install -r requirements-dev.txt
    python -m pytest --cov=common --cov=gateway --cov=cloud --cov=device --cov-report=term-missing
    python tests/mutation_check.py     # injects 16 defects into a temp copy, checks the tests catch them
