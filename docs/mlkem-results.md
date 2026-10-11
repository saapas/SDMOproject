# ML-KEM benchmark results (hybrid-ml-kem-768-x25519-aesgcm)

Environment: Windows, CPython 3.13.2, local Uvicorn cloud/gateway services
(same environment as the matched legacy run)

| Metric | Value |
|---|---|
| Handshake mean / p50 / p95 | 2.229 / 2.07 / 2.775 ms (n=200) |
| Message latency mean / p50 / p95 | 17.834 / 11.182 / 33.505 ms (n=500) |
| Throughput | 100.0 msg/s (20 devices, 500 msgs) |
| Handshake request / response size | 1696 / 1623 bytes |
| Public material on the wire (raw) | client 1216 B, server response 1120 B |
| Telemetry request size | 237 bytes |
| Crypto only: keygen / encapsulate+decapsulate | 263.5 / 433.3 us |

Handshake time includes the HTTP round trip plus client-side ML-KEM decapsulation
and X25519 derivation. Message latency includes the gateway -> cloud hop and the
SQLite write. Sample counts and settings match the legacy benchmark.
