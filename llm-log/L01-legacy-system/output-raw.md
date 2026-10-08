# Raw LLM output: L01

Here's a deliberately small project that still hits every requirement.

The concept: "Hybrid-handshake sensor pipeline"

Legacy system (you build or are given):

A simulated device (Python script) sends temperature readings every few seconds
An edge gateway (small Flask/FastAPI app) receives them and forwards to the cloud
A cloud service (another small Flask/FastAPI app) stores the readings in memory or SQLite and exposes them via an endpoint
Legacy key establishment: a pre-shared key, or classic X25519 ECDH, used to derive an AES-GCM session key

Your change: add ML-KEM to one communication path only, device → gateway. Leave gateway → cloud on TLS as-is, and document that as a known limitation.

Why this scope works
One path is enough per the brief ("at least one relevant communication path")
Python keeps everyone productive: liboqs-python (Open Quantum Safe) provides ML-KEM, so you never touch crypto internals
Everything runs in Docker Compose, which makes the test environment and CI trivial
ML-KEM design (keep it simple)
Hybrid handshake: the gateway advertises its ML-KEM-768 public key. The device encapsulates, gets a shared secret and ciphertext, and sends the ciphertext. Both sides run HKDF over (ML-KEM secret ‖ X25519 secret) to derive an AES-256-GCM key.
Fallback for legacy devices: the gateway accepts a protocol_version field. v1 devices keep working with the old method, and v2 devices use hybrid. Add a config flag ALLOW_LEGACY=true/false so you can show a migration plan (phase 1: allow both and log legacy use; phase 2: warn; phase 3: reject legacy).
Downgrade protection: include the version in the HKDF context so an attacker can't silently force v1.

The migration strategy and the downgrade discussion basically write your report's design section for you.

Work packages (7 weeks)
Week	Focus
1	Run baseline system, draw architecture, record baseline latency and handshake time
2	LLM generates tests and Dockerfiles; you review and fix
3	LLM proposes the ML-KEM integration; review it critically (check nonce reuse, key derivation, error handling)
4	Implement the final version, add tests including failure cases (bad ciphertext, replay, downgrade)
5	CI/CD (GitHub Actions: lint, test, build images, docker-compose deploy to a test environment)
6	Monitoring: /health endpoint, structured JSON logs, Prometheus metrics
7	Final measurements, risk analysis, report, demo
Minimal observability (the "PQ-related" part)

Expose a few Prometheus counters or just a /metrics endpoint:

handshakes_total{suite="mlkem768+x25519"} vs {suite="legacy"}
handshake_failures_total
handshake_duration_seconds
legacy_clients_active

The legacy-versus-PQ ratio is the metric that shows migration progress, which is a nice story for the demo.

CI/CD (keep it small)

One GitHub Actions workflow: ruff (lint) → bandit (static security analysis) → pytest → docker compose build → docker compose up plus a smoke test hitting /health. "Deploy to test environment" can just be Compose on a VM or a GitHub runner.

LLM evaluation (where the marks probably are)

Pick 3-4 artefacts for the LLM, and log prompt, output, and your decision for each:

Test suite: check whether the tests actually assert anything meaningful. Try mutation testing or deliberately break the code and see if tests fail.
Dockerfile / CI file: look for running as root, unpinned images, and secrets in the config.
ML-KEM integration: this is the most interesting. LLMs commonly misuse the library API, skip the KDF and use the raw shared secret as a key, reuse nonces, or hallucinate function names. Document what you found.
Metrics/logging: check that it doesn't log secrets or key material.

A table with columns Artefact | Prompt | What LLM produced | Issues found (and how) | Accepted/Modified/Rejected | Remaining risk covers the reporting requirement cleanly.

Things to deliberately skip
Mutual authentication or certificates (note it as technical debt)
ML-KEM on the gateway → cloud hop
Real hardware or a real database
Kubernetes (Compose is enough)
Performance tuning beyond a simple before/after handshake benchmark
Risks to mention in your final evaluation
liboqs is documented as not yet production-ready, so it's fine for a course but worth stating
No authentication means the handshake is not protected against active man-in-the-middle attacks
Constant-time and side-channel properties depend on the library, not your code
Real constrained devices may lack the RAM or CPU for ML-KEM-768

If you'd like, I can sketch the repo structure, the handshake message format, or a prompt template for logging your LLM interactions.
