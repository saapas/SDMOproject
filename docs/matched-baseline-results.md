# Baseline results (legacy-x25519-aesgcm)

Environment: Windows, CPython 3.13.2, local Uvicorn cloud/gateway services
(same environment as the matched ML-KEM run)

| Metric | Value |
|---|---|
| Handshake mean / p50 / p95 | 1.579 / 1.462 / 1.909 ms (n=200) |
| Message latency mean / p50 / p95 | 19.309 / 12.086 / 32.154 ms (n=500) |
| Throughput | 102.3 msg/s (20 devices, 500 msgs) |
| Handshake request / response size | 87 / 140 bytes |
| Public keys on the wire (raw) | client 32 B, server 32 B |
| Telemetry request size | 241 bytes |
| Crypto only: keygen / derive | 36.6 / 40.5 us |

Handshake time includes the HTTP round trip plus client-side key generation and derivation.
Message latency includes the gateway -> cloud hop and the SQLite write.
