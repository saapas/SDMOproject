# Baseline risk register

| ID | Weakness | Impact | Planned handling |
|---|---|---|---|
| R1 | X25519 only: not quantum-safe (harvest-now-decrypt-later) | Recorded traffic decryptable later | **Hybrid ML-KEM-768 + X25519** on device->gateway |
| R2 | Gateway not authenticated in handshake | Active MITM can impersonate the gateway | Out of scope; document as technical debt |
| R3 | No replay protection, no session expiry | Replayed messages accepted; sessions accumulate | Optional: counters/expiry; at least document |
| R4 | Gateway->cloud is plaintext HTTP | Data readable/modifiable on that hop | Out of scope; document |
| R5 | Sessions in memory only | Gateway restart drops all sessions (devices re-handshake) | Accept; measure impact |
| R6 | No tests | Regressions undetected | LLM-generated tests, reviewed + mutation-checked (MITIGATED)|
| R7 | No CI/CD | No automated build/test/deploy | GitHub Actions |
| R8 | No metrics or structured logs | No visibility into PQ migration | `/metrics`, JSON logs |
| R9 | Containers run as root, unpinned deps | Larger blast radius, non-reproducible builds | Harden Dockerfiles |
| R10 | Unbounded `sessions` dict | Memory exhaustion by handshake flooding | Add limit/TTL or document |
| R11 | Version not bound into key derivation yet | Future downgrade attacks | Include version/suite in HKDF context + transcript |
| R12 | No device authentication: anyone can handshake as any `device_id`; gateway forwards the `device_id` inside the plaintext without checking it against the session | Device impersonation / data poisoning | Document; bind device identity (pre-provisioned key or certificate) as future work |
