# Baseline architecture (legacy, pre-PQC)

```mermaid
flowchart LR
    D1[sensor-001] -->|"HTTP + X25519/AES-GCM payload"| G[Edge gateway :8080]
    D2[sensor-002] --> G
    D3[sensor-003] --> G
    G -->|"plain HTTP, plaintext JSON"| C[Cloud API :8000]
    C --> DB[(SQLite /data)]
```

## Components
| Component | Role | State |
|---|---|---|
| Device (`device/device.py`) | Generates readings every 3 s, runs the handshake, encrypts payloads | Ephemeral X25519 key; session key in memory |
| Gateway (`gateway/gateway.py`) | `/handshake`, `/telemetry`, `/health`; decrypts and forwards | In-memory `sessions` dict |
| Cloud (`cloud/cloud.py`) | `/readings`, `/health`; stores readings | SQLite on a volume |
| Crypto (`common/kex_legacy.py`) | X25519 ECDH, HKDF-SHA256, AES-256-GCM | Stateless |

## Handshake and data flow
```mermaid
sequenceDiagram
    participant D as Device
    participant G as Gateway
    participant C as Cloud
    D->>G: POST /handshake {device_id, client_pub}
    G-->>D: {session_id, server_pub, suite}
    Note over D,G: both derive key = HKDF(X25519 secret, info="suite|device_id")
    D->>G: POST /telemetry {session_id, nonce, ciphertext}
    G->>C: POST /readings (plaintext JSON)
    C-->>G: 201
    G-->>D: 202
```

## Trust boundaries
- Device <-> gateway: payload encrypted, **but the gateway is not authenticated**.
- Gateway <-> cloud: **no encryption, no authentication**.
- Cloud storage: plaintext in SQLite.

## Where quantum risk sits
X25519 is broken by a quantum computer (Shor). Anyone recording device<->gateway traffic today can decrypt it later
("harvest now, decrypt later"). Only the device<->gateway handshake is in scope for ML-KEM.
