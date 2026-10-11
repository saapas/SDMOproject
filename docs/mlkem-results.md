# ML-KEM benchmark results (hybrid-ml-kem-768-x25519-aesgcm)

Machine / Docker settings: _fill in (CPU, RAM, Docker Desktop backend)_

| Metric | Value |
|---|---|
| Handshake mean / p50 / p95 | 43.685 / 43.765 / 44.107 ms (n=200) |
| Message latency mean / p50 / p95 | 48.85 / 48.066 / 51.493 ms (n=500) |
| Throughput | 173.8 msg/s (20 devices, 500 msgs) |
| Handshake request / response size | 1696 / 1623 bytes |
| Public material on the wire (raw) | client 1216 B, server response 1120 B |
| Telemetry request size | 241 bytes |
| Crypto only: keygen / encapsulate+decapsulate | 110.7 / 220.8 us |

Handshake time includes the HTTP round trip plus client-side ML-KEM decapsulation
and X25519 derivation. Message latency includes the gateway -> cloud hop and the
SQLite write. Sample counts and settings match the legacy benchmark.
