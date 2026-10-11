# Evidence — AI drift audit, SDMOproject @ 1c80362 (2026-10-11)

Raw output behind [report.md](report.md). Sections 1–3 were produced by the audit run; section 4 by the reviewer.

> Note: sections 1–2 come from the first version of `locate.py`, which searched the working tree.
> The tree then contained this audit's own uncommitted L06 log files, so a few "llm-log at HEAD"
> counts include them. The current helper searches the committed HEAD only. No finding relies on those rows.

## 1. `locate.py` — first batch (with both PDFs as `--external`)

```text
Repository HEAD: 1c80362 (ai-drift-audit)

## ALLOW_LEGACY

| Category | Matches at HEAD | Commits where present (any branch) | First seen |
|---|---|---|---|
| code | 0 | 0 | - |
| tests | 0 | 0 | - |
| docs | 0 | 0 | - |
| llm-log | 2 | 36 | ab49a8e (2026-10-08) |
| other | 0 | 0 | - |
| external: Project Report Group 19.pdf | 2 | n/a | p.2, p.4 |
| external: Technical Documentation.pdf | 1 | n/a | p.2 |

- [llm-log] llm-log/L01-legacy-system/output3-raw.md:37: gateway.handshake(): add a protocol_version field, and keep the v1 path behind an ALLOW_LEGACY flag.
- [llm-log] llm-log/README.md:18: | L06 | AI drift audit skill | [L06-ai-drift-audit](L06-ai-drift-audit/entry.md) | [ ] | Features the LLM reco

> Hint: described but NEVER in code in any commit. Confirm by reading the code before reporting.

## protocol_version

| Category | Matches at HEAD | Commits where present (any branch) | First seen |
|---|---|---|---|
| code | 0 | 0 | - |
| tests | 0 | 0 | - |
| docs | 0 | 0 | - |
| llm-log | 2 | 36 | ab49a8e (2026-10-08) |
| other | 0 | 0 | - |
| external: Project Report Group 19.pdf | 2 | n/a | p.4, p.5 |
| external: Technical Documentation.pdf | 1 | n/a | p.2 |

- [llm-log] llm-log/L01-legacy-system/output-raw.md:48: PQC upgrade: add a hybrid ML-KEM-768 + X25519 handshake from an existing library (for example liboqs), with a 
- [llm-log] llm-log/L01-legacy-system/output3-raw.md:37: gateway.handshake(): add a protocol_version field, and keep the v1 path behind an ALLOW_LEGACY flag.

> Hint: described but NEVER in code in any commit. Confirm by reading the code before reporting.

## handshakes_total

| Category | Matches at HEAD | Commits where present (any branch) | First seen |
|---|---|---|---|
| code | 0 | 0 | - |
| tests | 0 | 0 | - |
| docs | 0 | 0 | - |
| llm-log | 0 | 8 | ab49a8e (2026-10-08) |
| other | 0 | 0 | - |
| external: Project Report Group 19.pdf | 0 | n/a | - |
| external: Technical Documentation.pdf | 1 | n/a | p.3 |


> Hint: described but NEVER in code in any commit. Confirm by reading the code before reporting.

## handshake_failures_total

| Category | Matches at HEAD | Commits where present (any branch) | First seen |
|---|---|---|---|
| code | 0 | 0 | - |
| tests | 0 | 0 | - |
| docs | 0 | 0 | - |
| llm-log | 0 | 8 | ab49a8e (2026-10-08) |
| other | 0 | 0 | - |
| external: Project Report Group 19.pdf | 0 | n/a | - |
| external: Technical Documentation.pdf | 1 | n/a | p.4 |


> Hint: described but NEVER in code in any commit. Confirm by reading the code before reporting.

## handshake_duration_seconds

| Category | Matches at HEAD | Commits where present (any branch) | First seen |
|---|---|---|---|
| code | 0 | 0 | - |
| tests | 0 | 0 | - |
| docs | 0 | 0 | - |
| llm-log | 0 | 8 | ab49a8e (2026-10-08) |
| other | 0 | 0 | - |
| external: Project Report Group 19.pdf | 0 | n/a | - |
| external: Technical Documentation.pdf | 1 | n/a | p.4 |


> Hint: described but NEVER in code in any commit. Confirm by reading the code before reporting.

## legacy_clients_active

| Category | Matches at HEAD | Commits where present (any branch) | First seen |
|---|---|---|---|
| code | 0 | 0 | - |
| tests | 0 | 0 | - |
| docs | 0 | 0 | - |
| llm-log | 0 | 8 | ab49a8e (2026-10-08) |
| other | 0 | 0 | - |
| external: Project Report Group 19.pdf | 0 | n/a | - |
| external: Technical Documentation.pdf | 1 | n/a | p.4 |


> Hint: described but NEVER in code in any commit. Confirm by reading the code before reporting.

## /metrics

| Category | Matches at HEAD | Commits where present (any branch) | First seen |
|---|---|---|---|
| code | 0 | 0 | - |
| tests | 0 | 0 | - |
| docs | 1 | 45 | ab42fd5 (2026-10-08) |
| llm-log | 0 | 8 | ab49a8e (2026-10-08) |
| other | 0 | 0 | - |
| external: Project Report Group 19.pdf | 0 | n/a | - |
| external: Technical Documentation.pdf | 0 | n/a | - |

- [docs] docs/risk-register.md:12: | R8 | No metrics or structured logs | No visibility into PQ migration | `/metrics`, JSON logs |

> Hint: described but NEVER in code in any commit. Confirm by reading the code before reporting.

## prometheus

| Category | Matches at HEAD | Commits where present (any branch) | First seen |
|---|---|---|---|
| code | 0 | 0 | - |
| tests | 0 | 0 | - |
| docs | 0 | 0 | - |
| llm-log | 1 | 36 | ab49a8e (2026-10-08) |
| other | 0 | 0 | - |
| external: Project Report Group 19.pdf | 0 | n/a | - |
| external: Technical Documentation.pdf | 0 | n/a | - |

- [llm-log] llm-log/L01-legacy-system/output-raw.md:47: Monitoring: /health endpoints, structured JSON logs and Prometheus metrics, including handshake counts per sui

> Hint: described but NEVER in code in any commit. Confirm by reading the code before reporting.

## structured

| Category | Matches at HEAD | Commits where present (any branch) | First seen |
|---|---|---|---|
| code | 0 | 0 | - |
| tests | 0 | 0 | - |
| docs | 2 | 46 | 3dd70b4 (2026-10-08) |
| llm-log | 3 | 36 | ab49a8e (2026-10-08) |
| other | 0 | 0 | - |
| external: Project Report Group 19.pdf | 0 | n/a | - |
| external: Technical Documentation.pdf | 0 | n/a | - |

- [docs] README.md:14: - no tests, no CI/CD, no metrics/structured logs
- [docs] docs/risk-register.md:12: | R8 | No metrics or structured logs | No visibility into PQ migration | `/metrics`, JSON logs |
- [llm-log] llm-log/L01-legacy-system/output-raw.md:30: Monitoring	No metrics, no structured logs, only simple print statements
- [llm-log] llm-log/L01-legacy-system/output-raw.md:47: Monitoring: /health endpoints, structured JSON logs and Prometheus metrics, including handshake counts per sui
- [llm-log] llm-log/L01-legacy-system/output3-raw.md:30: No tests, CI/CD, metrics or structured logs.

> Hint: described but NEVER in code in any commit. Confirm by reading the code before reporting.

## json log

| Category | Matches at HEAD | Commits where present (any branch) | First seen |
|---|---|---|---|
| code | 0 | 0 | - |
| tests | 0 | 0 | - |
| docs | 1 | 45 | ab42fd5 (2026-10-08) |
| llm-log | 1 | 36 | ab49a8e (2026-10-08) |
| other | 0 | 0 | - |
| external: Project Report Group 19.pdf | 0 | n/a | - |
| external: Technical Documentation.pdf | 0 | n/a | - |

- [docs] docs/risk-register.md:12: | R8 | No metrics or structured logs | No visibility into PQ migration | `/metrics`, JSON logs |
- [llm-log] llm-log/L01-legacy-system/output-raw.md:47: Monitoring: /health endpoints, structured JSON logs and Prometheus metrics, including handshake counts per sui

> Hint: described but NEVER in code in any commit. Confirm by reading the code before reporting.

## logging

| Category | Matches at HEAD | Commits where present (any branch) | First seen |
|---|---|---|---|
| code | 0 | 0 | - |
| tests | 0 | 0 | - |
| docs | 0 | 0 | - |
| llm-log | 2 | 42 | 394a632 (2026-10-08) |
| other | 0 | 0 | - |
| external: Project Report Group 19.pdf | 0 | n/a | - |
| external: Technical Documentation.pdf | 1 | n/a | p.5 |

- [llm-log] llm-log/L05-metrics-logging/entry.md:1: # L05: Metrics and logging
- [llm-log] llm-log/README.md:17: | L05 | Metrics and logging | [L05-metrics-logging](L05-metrics-logging/entry.md) | [ ] | [ ] | [ ] |

> Hint: described but NEVER in code in any commit. Confirm by reading the code before reporting.

## fallback

| Category | Matches at HEAD | Commits where present (any branch) | First seen |
|---|---|---|---|
| code | 0 | 0 | - |
| tests | 0 | 0 | - |
| docs | 0 | 0 | - |
| llm-log | 1 | 36 | ab49a8e (2026-10-08) |
| other | 0 | 0 | - |
| external: Project Report Group 19.pdf | 1 | n/a | p.5 |
| external: Technical Documentation.pdf | 2 | n/a | p.1, p.2 |

- [llm-log] llm-log/L01-legacy-system/output3-raw.md:38: device.handshake(): do the v2 flow, with fallback to v1.

> Hint: described but NEVER in code in any commit. Confirm by reading the code before reporting.

## downgrade

| Category | Matches at HEAD | Commits where present (any branch) | First seen |
|---|---|---|---|
| code | 0 | 0 | - |
| tests | 0 | 0 | - |
| docs | 1 | 45 | ab42fd5 (2026-10-08) |
| llm-log | 0 | 37 | 394a632 (2026-10-08) |
| other | 0 | 0 | - |
| external: Project Report Group 19.pdf | 1 | n/a | p.4 |
| external: Technical Documentation.pdf | 2 | n/a | p.2, p.4 |

- [docs] docs/risk-register.md:15: | R11 | Version not bound into key derivation yet | Future downgrade attacks | Include version/suite in HKDF c

> Hint: described but NEVER in code in any commit. Confirm by reading the code before reporting.

## transcript

| Category | Matches at HEAD | Commits where present (any branch) | First seen |
|---|---|---|---|
| code | 0 | 0 | - |
| tests | 0 | 0 | - |
| docs | 1 | 45 | ab42fd5 (2026-10-08) |
| llm-log | 0 | 0 | - |
| other | 0 | 0 | - |
| external: Project Report Group 19.pdf | 0 | n/a | - |
| external: Technical Documentation.pdf | 0 | n/a | - |

- [docs] docs/risk-register.md:15: | R11 | Version not bound into key derivation yet | Future downgrade attacks | Include version/suite in HKDF c

> Hint: described but NEVER in code in any commit. Confirm by reading the code before reporting.

## project-report

| Category | Matches at HEAD | Commits where present (any branch) | First seen |
|---|---|---|---|
| code | 0 | 0 | - |
| tests | 0 | 0 | - |
| docs | 1 | 2 | 8a29a42 (2026-10-11) |
| llm-log | 1 | 4 | cc2ee4a (2026-10-11) |
| other | 0 | 0 | - |
| external: Project Report Group 19.pdf | 1 | n/a | p.1 |
| external: Technical Documentation.pdf | 0 | n/a | - |

- [docs] README.md:123: `docs/project-report.md`. Run each benchmark multiple times and compare
- [llm-log] llm-log/L04-mlkem-integration/output-raw.md:15: Added a report-ready test-results table to docs/project-report.md.

> Hint: described but NEVER in code in any commit. Confirm by reading the code before reporting.

## liboqs

| Category | Matches at HEAD | Commits where present (any branch) | First seen |
|---|---|---|---|
| code | 0 | 0 | - |
| tests | 0 | 0 | - |
| docs | 0 | 0 | - |
| llm-log | 3 | 36 | ab49a8e (2026-10-08) |
| other | 0 | 0 | - |
| external: Project Report Group 19.pdf | 0 | n/a | - |
| external: Technical Documentation.pdf | 1 | n/a | p.2 |

- [llm-log] llm-log/L01-legacy-system/output-raw.md:48: PQC upgrade: add a hybrid ML-KEM-768 + X25519 handshake from an existing library (for example liboqs), with a 
- [llm-log] llm-log/L03-ci-workflow/output-raw.md:36: When liboqs arrives, the Docker build gets slower and more fragile because of the native library. Cache the im
- [llm-log] llm-log/L03-ci-workflow/output2-raw.md:58: When you’re ready for the PQC work, I’d start by checking that liboqs-python builds in the Docker image, becau

> Hint: described but NEVER in code in any commit. Confirm by reading the code before reporting.

## pqcrypto

| Category | Matches at HEAD | Commits where present (any branch) | First seen |
|---|---|---|---|
| code | 6 | 4 | 1ac7de3 (2026-10-11) |
| tests | 0 | 0 | - |
| docs | 0 | 0 | - |
| llm-log | 1 | 4 | cc2ee4a (2026-10-11) |
| other | 0 | 0 | - |
| external: Project Report Group 19.pdf | 0 | n/a | - |
| external: Technical Documentation.pdf | 0 | n/a | - |

- [code] bench/requirements.txt:3: pqcrypto==0.3.4
- [code] common/kex_mlkem.py:11: from pqcrypto.kem.ml_kem_768 import decrypt as kem_decrypt
- [code] common/kex_mlkem.py:12: from pqcrypto.kem.ml_kem_768 import encrypt as kem_encrypt
- [code] common/kex_mlkem.py:13: from pqcrypto.kem.ml_kem_768 import generate_keypair as kem_generate_keypair
- [code] device/requirements.txt:2: pqcrypto==0.3.4
- [code] gateway/requirements.txt:4: pqcrypto==0.3.4
- [llm-log] llm-log/L04-mlkem-integration/output-raw.md:9: Added pinned pqcrypto==0.3.4 dependencies to:

## sha256:

| Category | Matches at HEAD | Commits where present (any branch) | First seen |
|---|---|---|---|
| code | 0 | 0 | - |
| tests | 0 | 0 | - |
| docs | 0 | 0 | - |
| llm-log | 1 | 7 | a7e42a7 (2026-10-10) |
| other | 0 | 0 | - |
| external: Project Report Group 19.pdf | 0 | n/a | - |
| external: Technical Documentation.pdf | 0 | n/a | - |

- [llm-log] llm-log/L03-ci-workflow/output2-raw.md:53: Pin the base image by digest (python:3.12-slim@sha256:...). Pull the image and read the digest, since I can’t.

> Hint: described but NEVER in code in any commit. Confirm by reading the code before reporting.

## kem_public_key

| Category | Matches at HEAD | Commits where present (any branch) | First seen |
|---|---|---|---|
| code | 9 | 4 | 1ac7de3 (2026-10-11) |
| tests | 2 | 4 | 1ac7de3 (2026-10-11) |
| docs | 0 | 0 | - |
| llm-log | 0 | 0 | - |
| other | 0 | 0 | - |
| external: Project Report Group 19.pdf | 0 | n/a | - |
| external: Technical Documentation.pdf | 0 | n/a | - |

- [code] bench/mlkem.py:49: "kem_public_key": b64(kem_public),
- [code] common/kex_mlkem.py:16: KEM_PUBLIC_KEY_BYTES = 1184
- [code] common/kex_mlkem.py:34: if len(peer_kem_public) != KEM_PUBLIC_KEY_BYTES:
- [code] common/kex_mlkem.py:35: raise ValueError("invalid ML-KEM public key length")
- [code] device/device.py:27: "kem_public_key": b64(kem_public),
- [code] gateway/gateway.py:28: kem_public_key: str | None = None
- [tests] tests/test_kex_mlkem.py:22: assert len(public) == kex.KEM_PUBLIC_KEY_BYTES
- [tests] tests/test_kex_mlkem.py:48: [(b"short", b"x" * 32), (b"x" * kex.KEM_PUBLIC_KEY_BYTES, b"short")],

```

## 2. `locate.py` — second batch

```text
Repository HEAD: 1c80362 (ai-drift-audit)

## cloud-data

| Category | Matches at HEAD | Commits where present (any branch) | First seen |
|---|---|---|---|
| code | 2 | 10 | 3f76ac0 (2026-10-10) |
| tests | 0 | 0 | - |
| docs | 0 | 0 | - |
| llm-log | 1 | 7 | a7e42a7 (2026-10-10) |
| other | 0 | 0 | - |
| external: Project Report Group 19.pdf | 0 | n/a | - |
| external: Technical Documentation.pdf | 0 | n/a | - |

- [code] docker-compose.yml:5: volumes: ["cloud-data:/data"]
- [code] docker-compose.yml:46: cloud-data:
- [llm-log] llm-log/L03-ci-workflow/output2-raw.md:50: ./data became a named volume (cloud-data). A bind mount would be owned by the runner’s user and the non-root c

## xfail

| Category | Matches at HEAD | Commits where present (any branch) | First seen |
|---|---|---|---|
| code | 0 | 0 | - |
| tests | 2 | 32 | 43a90ce (2026-10-09) |
| docs | 0 | 15 | 43a90ce (2026-10-09) |
| llm-log | 1 | 30 | c1408be (2026-10-09) |
| other | 0 | 0 | - |
| external: Project Report Group 19.pdf | 0 | n/a | - |
| external: Technical Documentation.pdf | 1 | n/a | p.4 |

- [tests] tests/test_gateway.py:176: @pytest.mark.xfail(reason="R3: no replay protection in the legacy baseline", strict=False)
- [tests] tests/test_gateway.py:184: @pytest.mark.xfail(reason="R10: session table is unbounded in the legacy baseline", strict=False)
- [llm-log] llm-log/L02-tests/output-raw.md:17: Two tests are marked xfail: replay protection (R3) and the unbounded session table (R10). They document weakne

## GPT 5.6

| Category | Matches at HEAD | Commits where present (any branch) | First seen |
|---|---|---|---|
| code | 0 | 0 | - |
| tests | 0 | 0 | - |
| docs | 0 | 0 | - |
| llm-log | 1 | 5 | b4152e3 (2026-10-11) |
| other | 0 | 0 | - |
| external: Project Report Group 19.pdf | 0 | n/a | - |
| external: Technical Documentation.pdf | 0 | n/a | - |

- [llm-log] llm-log/L04-mlkem-integration/entry.md:3: - **LLM and version:** GPT 5.6 Luna

> Hint: described but NEVER in code in any commit. Confirm by reading the code before reporting.

## Claude Sonnet

| Category | Matches at HEAD | Commits where present (any branch) | First seen |
|---|---|---|---|
| code | 0 | 0 | - |
| tests | 0 | 0 | - |
| docs | 0 | 0 | - |
| llm-log | 7 | 40 | 60489f6 (2026-10-08) |
| other | 0 | 0 | - |
| external: Project Report Group 19.pdf | 0 | n/a | - |
| external: Technical Documentation.pdf | 1 | n/a | p.4 |

- [llm-log] llm-log/L01-legacy-system/entry.md:3: - **LLM and version:** Claude Sonnet 5.5
- [llm-log] llm-log/L01-legacy-system/entry2.md:3: - **LLM and version:** Claude Sonnet 5.5
- [llm-log] llm-log/L01-legacy-system/entry3.md:3: - **LLM and version:** Claude Sonnet 5.5
- [llm-log] llm-log/L02-tests/entry.md:3: - **LLM and version:** Claude Sonnet 5.5

> Hint: described but NEVER in code in any commit. Confirm by reading the code before reporting.

## warn

| Category | Matches at HEAD | Commits where present (any branch) | First seen |
|---|---|---|---|
| code | 2 | 32 | 43a90ce (2026-10-09) |
| tests | 0 | 0 | - |
| docs | 0 | 0 | - |
| llm-log | 1 | 15 | ab49a8e (2026-10-08) |
| other | 0 | 0 | - |
| external: Project Report Group 19.pdf | 1 | n/a | p.4 |
| external: Technical Documentation.pdf | 1 | n/a | p.2 |

- [code] pytest.ini:5: filterwarnings =
- [code] pytest.ini:6: ignore::DeprecationWarning
- [llm-log] llm-log/L03-ci-workflow/output2-raw.md:3: The smoke test passes against a live stack and fails correctly when the gateway is down. I’ll fix a small comm

## @v4

| Category | Matches at HEAD | Commits where present (any branch) | First seen |
|---|---|---|---|
| code | 7 | 10 | 3f76ac0 (2026-10-10) |
| tests | 0 | 0 | - |
| docs | 0 | 0 | - |
| llm-log | 1 | 7 | a7e42a7 (2026-10-10) |
| other | 0 | 0 | - |
| external: Project Report Group 19.pdf | 0 | n/a | - |
| external: Technical Documentation.pdf | 0 | n/a | - |

- [code] .github/workflows/ci.yml:19: - uses: actions/checkout@v4
- [code] .github/workflows/ci.yml:31: - uses: actions/checkout@v4
- [code] .github/workflows/ci.yml:49: - uses: actions/checkout@v4
- [code] .github/workflows/ci.yml:61: - uses: actions/upload-artifact@v4
- [llm-log] llm-log/L03-ci-workflow/output2-raw.md:53: Pin the base image by digest (python:3.12-slim@sha256:...). Pull the image and read the digest, since I can’t.

## kex_mlkem

| Category | Matches at HEAD | Commits where present (any branch) | First seen |
|---|---|---|---|
| code | 5 | 4 | 1ac7de3 (2026-10-11) |
| tests | 1 | 4 | 1ac7de3 (2026-10-11) |
| docs | 1 | 4 | 1ac7de3 (2026-10-11) |
| llm-log | 2 | 4 | cc2ee4a (2026-10-11) |
| other | 0 | 0 | - |
| external: Project Report Group 19.pdf | 0 | n/a | - |
| external: Technical Documentation.pdf | 0 | n/a | - |

- [code] bench/mlkem.py:19: from common import kex_mlkem as kex  # noqa: E402
- [code] device/device.py:10: from common import kex_mlkem as kex
- [code] gateway/gateway.py:13: from common import kex_mlkem
- [code] gateway/gateway.py:58: key, kem_ciphertext, server_pub = kex_mlkem.encapsulate(
- [tests] tests/test_kex_mlkem.py:5: from common import kex_mlkem as kex
- [docs] README.md:8: Key exchange code: `common/kex_mlkem.py` implements the default hybrid
- [llm-log] llm-log/L04-mlkem-integration/output-raw.md:4: Added hybrid ML-KEM-768 + X25519 implementation in common/kex_mlkem.py.
- [llm-log] llm-log/L04-mlkem-integration/output-raw.md:13: Added ML-KEM tests in tests/test_kex_mlkem.py.

## USER app

| Category | Matches at HEAD | Commits where present (any branch) | First seen |
|---|---|---|---|
| code | 3 | 10 | 3f76ac0 (2026-10-10) |
| tests | 0 | 0 | - |
| docs | 0 | 0 | - |
| llm-log | 0 | 0 | - |
| other | 0 | 0 | - |
| external: Project Report Group 19.pdf | 0 | n/a | - |
| external: Technical Documentation.pdf | 0 | n/a | - |

- [code] cloud/Dockerfile:9: USER app
- [code] device/Dockerfile:10: USER app
- [code] gateway/Dockerfile:10: USER app

## healthcheck

| Category | Matches at HEAD | Commits where present (any branch) | First seen |
|---|---|---|---|
| code | 2 | 10 | 3f76ac0 (2026-10-10) |
| tests | 0 | 0 | - |
| docs | 0 | 0 | - |
| llm-log | 4 | 11 | 41e743c (2026-10-09) |
| other | 0 | 0 | - |
| external: Project Report Group 19.pdf | 0 | n/a | - |
| external: Technical Documentation.pdf | 0 | n/a | - |

- [code] docker-compose.yml:7: healthcheck:
- [code] docker-compose.yml:20: healthcheck:
- [llm-log] llm-log/L03-ci-workflow/output-raw.md:20: Health checks: docker compose up --wait only works if the services declare healthcheck. Your compose file has 
- [llm-log] llm-log/L03-ci-workflow/output-raw.md:38: I can write the workflow, the compose healthchecks and the hardened Dockerfiles. I can test ruff, bandit, pip-
- [llm-log] llm-log/L03-ci-workflow/output2-raw.md:9: Not verified: the Docker build, the compose healthchecks and the GitHub Actions run. This sandbox has no Docke
- [llm-log] llm-log/L03-ci-workflow/output2-raw.md:48: Healthchecks on cloud and gateway use a one-line Python call, because the slim image has no curl.

## logger

| Category | Matches at HEAD | Commits where present (any branch) | First seen |
|---|---|---|---|
| code | 0 | 0 | - |
| tests | 0 | 0 | - |
| docs | 0 | 0 | - |
| llm-log | 0 | 0 | - |
| other | 0 | 0 | - |
| external: Project Report Group 19.pdf | 0 | n/a | - |
| external: Technical Documentation.pdf | 0 | n/a | - |


## approved

| Category | Matches at HEAD | Commits where present (any branch) | First seen |
|---|---|---|---|
| code | 0 | 0 | - |
| tests | 0 | 0 | - |
| docs | 0 | 0 | - |
| llm-log | 0 | 0 | - |
| other | 0 | 0 | - |
| external: Project Report Group 19.pdf | 1 | n/a | p.4 |
| external: Technical Documentation.pdf | 0 | n/a | - |


> Hint: described but NEVER in code in any commit. Confirm by reading the code before reporting.

## session limit

| Category | Matches at HEAD | Commits where present (any branch) | First seen |
|---|---|---|---|
| code | 0 | 0 | - |
| tests | 0 | 0 | - |
| docs | 0 | 0 | - |
| llm-log | 0 | 0 | - |
| other | 0 | 0 | - |
| external: Project Report Group 19.pdf | 0 | n/a | - |
| external: Technical Documentation.pdf | 0 | n/a | - |


```

## 3. Other commands run by the audit

```text
$ git rev-parse --short HEAD; git branch --show-current; git log --all --oneline | wc -l
1c80362
ai-drift-audit
      47

$ git status --short
 M llm-log/README.md
?? .claude/
?? audits/
?? llm-log/L06-ai-drift-audit/

$ git log --all --oneline -- docs/project-report.md   (empty = never existed)

$ git grep -n -E "ALLOW_LEGACY|protocol_version|getenv" HEAD -- gateway device common
HEAD:device/device.py:12:DEVICE_ID = os.getenv("DEVICE_ID", "sensor-001")
HEAD:device/device.py:13:SENSOR_TYPE = os.getenv("SENSOR_TYPE", "temperature")
HEAD:device/device.py:14:GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8080")
HEAD:device/device.py:15:INTERVAL = float(os.getenv("INTERVAL", "3"))
HEAD:gateway/gateway.py:15:CLOUD_URL = os.getenv("CLOUD_URL", "http://localhost:8000")
HEAD:gateway/gateway.py:16:GATEWAY_ID = os.getenv("GATEWAY_ID", "gateway-01")

$ git grep -n -E "info=" HEAD -- common
HEAD:common/kex_legacy.py:34:        info=f"{SUITE}|{device_id}".encode(),
HEAD:common/kex_mlkem.py:79:        info=f"{SUITE}|{device_id}".encode(),

$ git grep -n -i -E "metrics|prometheus|logging|logger" HEAD -- gateway device cloud common "*/requirements.txt"   (empty = none)

$ git grep -n "@app\." HEAD -- gateway cloud
HEAD:cloud/cloud.py:35:@app.get("/health")
HEAD:cloud/cloud.py:40:@app.post("/readings", status_code=201)
HEAD:cloud/cloud.py:52:@app.get("/readings")
HEAD:gateway/gateway.py:47:@app.get("/health")
HEAD:gateway/gateway.py:52:@app.post("/handshake")
HEAD:gateway/gateway.py:82:@app.post("/telemetry", status_code=202)

$ git grep -n -i downgrade $(git log --all --format=%h) -- tests   (empty = no downgrade test in any commit)

$ git grep -n -E "kem_public_key|kex_mlkem" HEAD -- tests
HEAD:tests/test_kex_mlkem.py:5:from common import kex_mlkem as kex

$ git grep -n "xfail" HEAD -- tests
HEAD:tests/test_gateway.py:176:@pytest.mark.xfail(reason="R3: no replay protection in the legacy baseline", strict=False)
HEAD:tests/test_gateway.py:184:@pytest.mark.xfail(reason="R10: session table is unbounded in the legacy baseline", strict=False)

$ git show 1793546:llm-log/L01-legacy-system/output-raw.md | sed -n "21,23p;38,45p"   (earlier raw L01 output, replaced in d362548)
Hybrid handshake: the gateway advertises its ML-KEM-768 public key. The device encapsulates, gets a shared secret and ciphertext, and sends the ciphertext. Both sides run HKDF over (ML-KEM secret ‖ X25519 secret) to derive an AES-256-GCM key.
Fallback for legacy devices: the gateway accepts a protocol_version field. v1 devices keep working with the old method, and v2 devices use hybrid. Add a config flag ALLOW_LEGACY=true/false so you can show a migration plan (phase 1: allow both and log legacy use; phase 2: warn; phase 3: reject legacy).
Downgrade protection: include the version in the HKDF context so an attacker can't silently force v1.
Expose a few Prometheus counters or just a /metrics endpoint:

handshakes_total{suite="mlkem768+x25519"} vs {suite="legacy"}
handshake_failures_total
handshake_duration_seconds
legacy_clients_active

The legacy-versus-PQ ratio is the metric that shows migration progress, which is a nice story for the demo.

$ git show 3f76ac0:bench/requirements.txt; cat bench/requirements.txt
requests>=2.31
cryptography>=42
...
requests>=2.31
cryptography>=42
pqcrypto==0.3.4

$ grep -n -E "pip-audit|^on:|branches|pull_request|if:|upload-artifact" .github/workflows/ci.yml
3:on:
5:    branches: [main]
6:  pull_request:
40:      - name: Dependency audit (pip-audit)
43:            pip-audit -r "$f/requirements.txt" --no-deps --disable-pip
61:      - uses: actions/upload-artifact@v4
78:        if: failure()
81:        if: always()

$ grep -n FROM */Dockerfile; grep -n "uses:" .github/workflows/*.yml
gateway/Dockerfile:2:FROM python:3.12-slim
cloud/Dockerfile:2:FROM python:3.12-slim
device/Dockerfile:2:FROM python:3.12-slim
.github/workflows/ci.yml:19:      - uses: actions/checkout@v4
.github/workflows/ci.yml:20:      - uses: actions/setup-python@v5
.github/workflows/ci.yml:31:      - uses: actions/checkout@v4
.github/workflows/ci.yml:32:      - uses: actions/setup-python@v5
.github/workflows/ci.yml:49:      - uses: actions/checkout@v4
.github/workflows/ci.yml:50:      - uses: actions/setup-python@v5
.github/workflows/ci.yml:61:      - uses: actions/upload-artifact@v4
.github/workflows/ci.yml:70:      - uses: actions/checkout@v4
.github/workflows/mutation.yml:16:      - uses: actions/checkout@v4
.github/workflows/mutation.yml:17:      - uses: actions/setup-python@v5
.github/workflows/mutation.yml:24:      - uses: actions/upload-artifact@v4

$ git tag -l
baseline-legacy

$ git show 1ac7de3:docs/mlkem-results.md | sed -n 7,14p   (numbers used in the report)
|---|---|
| Handshake mean / p50 / p95 | 2.229 / 2.07 / 2.775 ms (n=200) |
| Message latency mean / p50 / p95 | 17.834 / 11.182 / 33.505 ms (n=500) |
| Throughput | 100.0 msg/s (20 devices, 500 msgs) |
| Handshake request / response size | 1696 / 1623 bytes |
| Public material on the wire (raw) | client 1216 B, server response 1120 B |
| Telemetry request size | 237 bytes |
| Crypto only: keygen / encapsulate+decapsulate | 263.5 / 433.3 us |

$ sed -n 7,13p docs/mlkem-results.md   (HEAD, overwritten in 1c80362)
| Handshake mean / p50 / p95 | 43.685 / 43.765 / 44.107 ms (n=200) |
| Message latency mean / p50 / p95 | 48.85 / 48.066 / 51.493 ms (n=500) |
| Throughput | 173.8 msg/s (20 devices, 500 msgs) |
| Handshake request / response size | 1696 / 1623 bytes |
| Public material on the wire (raw) | client 1216 B, server response 1120 B |
| Telemetry request size | 241 bytes |
| Crypto only: keygen / encapsulate+decapsulate | 110.7 / 220.8 us |

$ git show baseline-legacy:docs/baseline-results.md | sed -n 7,9p   (numbers used in tech doc §2)
| Handshake mean / p50 / p95 | 43.744 / 43.939 / 44.301 ms (n=200) |
| Message latency mean / p50 / p95 | 56.163 / 56.042 / 58.27 ms (n=500) |
| Throughput | 93.4 msg/s (20 devices, 500 msgs) |
```

## 4. Reviewer verification

```text
$ git show 1793546:llm-log/L01-legacy-system/output-raw.md | grep -n -iE 'ALLOW_LEGACY|HKDF context|handshakes_total|handshake_failures_total|handshake_duration_seconds|legacy_clients_active'
22:Fallback for legacy devices: the gateway accepts a protocol_version field. v1 devices keep working with the old method, and v2 devices use hybrid. Add a config flag ALLOW_LEGACY=true/false so you can show a migration plan (phase 1: allow both and log legacy use; phase 2: warn; phase 3: reject legacy).
23:Downgrade protection: include the version in the HKDF context so an attacker can't silently force v1.
40:handshakes_total{suite="mlkem768+x25519"} vs {suite="legacy"}
41:handshake_failures_total
42:handshake_duration_seconds
43:legacy_clients_active

$ git log --format='%h %ad %s' --date=short -- llm-log/L01-legacy-system/output-raw.md
d362548 2026-10-09 actual entries
ab49a8e 2026-10-08 llm output
30c0345 2026-10-08 Updated llm-logs
867a61c 2026-10-08 Delete llm-log directory
fb69403 2026-10-08 Add files via upload

$ grep -n project-report README.md
123:`docs/project-report.md`. Run each benchmark multiple times and compare

$ git log --all --oneline -- docs/project-report.md
(no output)

$ git diff 1ac7de3 1c80362 -- docs/mlkem-results.md | grep -E '^[-+][|E]' | head -4
-Environment: Windows, CPython 3.13.2, local Uvicorn cloud/gateway services
-| Handshake mean / p50 / p95 | 2.229 / 2.07 / 2.775 ms (n=200) |
-| Message latency mean / p50 / p95 | 17.834 / 11.182 / 33.505 ms (n=500) |
-| Throughput | 100.0 msg/s (20 devices, 500 msgs) |

$ grep -c kem_public_key tests/test_gateway.py
0

$ grep -c kex_mlkem tests/mutation_check.py
0

$ grep -c '^    ("' tests/mutation_check.py
16

```
