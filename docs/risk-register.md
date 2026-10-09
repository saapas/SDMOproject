# Baseline risk register

| ID | Weakness | Impact | Planned handling |
|---|---|---|---|
| R1 | X25519 only. Not quantum-safe | Recorded traffic decryptable later | Hybrid ML-KEM + X25519 on device to gateway |
| R2 | Gateway not authenticated in handshake | Can impersonate the gateway | Made if there is time |
| R3 | No replay protection, no session expiry | Replayed messages accepted so sessions accumulate | Made if time |
| R4 | Gateway to cloud is plaintext HTTP | Data readable/modifiable on that hop | Made if time |
| R5 | Sessions in memory only | Gateway restart drops all sessions | Will see |
| R6 | No tests | Regressions undetected | LLM-generated tests, reviewed + mutation-checked (MITIGATED)|
| R7 | No CI/CD | No automated build/test/deploy | GitHub Actions |
| R8 | No metrics or structured logs | No visibility into PQ migration | `/metrics`, JSON logs |
| R9 | Containers run as root, unpinned deps | Larger blast radius, non-reproducible builds | Harden Dockerfiles |
| R10 | Unbounded `sessions` dict | Memory exhaustion by handshake flooding | Add limit/TTL or document |
| R11 | Version not bound into key derivation yet | Future downgrade attacks | Include version/suite in HKDF context + transcript |
