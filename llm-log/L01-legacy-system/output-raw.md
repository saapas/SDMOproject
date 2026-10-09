# Raw LLM output: L01

The concept: a deliberately incomplete sensor pipeline

I’d build a small three-tier system in Python that works end to end but is left unfinished in the ways you listed. It is meant to be upgraded later.

Components

Edge device: a Python script that simulates a sensor (temperature, humidity, pressure) and sends a reading every few seconds.
Edge gateway: a small FastAPI app that sets up a secure session with each device, decrypts the readings and forwards them to the cloud.
Cloud service: a second FastAPI app that stores readings in SQLite and exposes them through a REST endpoint.
Packaging: Docker Compose with one container per service, so the whole system starts with one command.
The outdated key establishment

Between the device and the gateway, I’d use a classic, pre-quantum mechanism:

The device and gateway each generate an ephemeral X25519 key pair and exchange public keys over HTTP (POST /handshake).
Both compute the shared secret, then derive a 256-bit key with HKDF-SHA256.
Every reading is encrypted with AES-256-GCM, using a fresh random nonce and the device ID as associated data.

This is a realistic legacy design: secure against today’s attackers, but vulnerable to “harvest now, decrypt later” once a quantum computer can break elliptic-curve key exchange. It’s also easy to upgrade later, because all the crypto lives in a single module (common/kex_legacy.py). When you move to PQC, you replace or extend that module and the two handshake functions.

What I’d leave out on purpose

This is what makes the system “legacy” and gives you the upgrade work:

Area	State in the legacy system
Tests	None
CI/CD	None, no pipeline
Monitoring	No metrics, no structured logs, only simple print statements
Key establishment	X25519 only, not quantum-safe
Gateway authentication	None (open to active man-in-the-middle)
Replay protection and session expiry	None, sessions kept in memory forever
Gateway → cloud hop	Plain HTTP
Containers	Run as root, unpinned dependencies

The system is functional, but each gap is a clear, bounded piece of work.

Why this scope works
Small enough to understand fully. Three services, a few hundred lines of code, and one place where the crypto lives.
Realistic enough to upgrade. It has an actual handshake, actual encryption, and a real data flow, not a toy stub.
Easy to run. docker compose up --build starts everything, which also gives you a test environment for later.
The upgrade path afterwards
Baseline: run it, draw the architecture, and measure handshake time, message latency and message sizes before changing anything.
Tests: unit tests for the crypto, API tests for gateway and cloud, failure cases (tampered messages, unknown sessions, cloud down).
CI/CD: a pipeline that lints, runs static security checks, runs the tests, builds the images and does a smoke test.
Monitoring: /health endpoints, structured JSON logs and Prometheus metrics, including handshake counts per suite.
PQC upgrade: add a hybrid ML-KEM-768 + X25519 handshake from an existing library (for example liboqs), with a protocol version field so legacy devices keep working during migration.

The metric that shows migration progress is the ratio of legacy to post-quantum handshakes.

Things I’d deliberately skip
Real hardware, a real database, or Kubernetes
Certificates and mutual authentication (note them as technical debt)
Post-quantum protection of the gateway → cloud hop in the first upgrade
Performance tuning beyond a before/after handshake benchmark
