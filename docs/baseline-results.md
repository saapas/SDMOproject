# Baseline results (legacy-x25519-aesgcm)

Machine / Docker settings: _fill in (CPU, RAM, Docker Desktop backend)_

| Metric | Value |
|---|---|
| Handshake mean / p50 / p95 | 43.744 / 43.939 / 44.301 ms (n=200) |
| Message latency mean / p50 / p95 | 56.163 / 56.042 / 58.27 ms (n=500) |
| Throughput | 93.4 msg/s (20 devices, 500 msgs) |
| Handshake request / response size | 87 / 140 bytes |
| Public keys on the wire (raw) | client 32 B, server 32 B |
| Telemetry request size | 241 bytes |
| Crypto only: keygen / derive | 25.7 / 27.2 us |

Handshake time includes the HTTP round trip plus client-side key generation and derivation.
Message latency includes the gateway -> cloud hop and the SQLite write.
