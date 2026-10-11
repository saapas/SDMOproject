# Baseline results (legacy-x25519-aesgcm)

Machine / Docker settings: _fill in (CPU, RAM, Docker Desktop backend)_

| Metric | Value |
|---|---|
| Handshake mean / p50 / p95 | 43.853 / 43.95 / 44.273 ms (n=200) |
| Message latency mean / p50 / p95 | 48.412 / 48.101 / 51.677 ms (n=500) |
| Throughput | 171.1 msg/s (20 devices, 500 msgs) |
| Handshake request / response size | 87 / 140 bytes |
| Public keys on the wire (raw) | client 32 B, server 32 B |
| Telemetry request size | 241 bytes |
| Crypto only: keygen / derive | 26.1 / 28.3 us |

Handshake time includes the HTTP round trip plus client-side key generation and derivation.
Message latency includes the gateway -> cloud hop and the SQLite write.
