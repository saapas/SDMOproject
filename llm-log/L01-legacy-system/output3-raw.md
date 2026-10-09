# Raw LLM output: L01

I’ve built the legacy baseline as a small Python project. I ran it locally (not in Docker) and it works end to end: the device handshakes, sends encrypted readings, and the gateway decrypts and forwards them to the cloud, which stores them in SQLite.

What’s in it
legacy-pqc/
├── common/kex_legacy.py   # X25519 + HKDF + AES-256-GCM (the part you'll replace with ML-KEM)
├── device/device.py       # simulated sensor: handshake, then encrypted readings
├── gateway/gateway.py     # FastAPI: /handshake, /telemetry, /health
├── cloud/cloud.py         # FastAPI + SQLite: /readings, /health
├── */Dockerfile, */requirements.txt
├── docker-compose.yml     # cloud, gateway, 3 sensors
└── README.md

Run it: docker compose up --build, then curl localhost:8000/readings.

How it works
The device generates an ephemeral X25519 key and POSTs it to /handshake.
The gateway generates its own ephemeral key and returns it with a session_id. Both sides derive the AES-256 key via HKDF.
The device sends {session_id, nonce, ciphertext} to /telemetry, with the device ID as the GCM associated data.
The gateway decrypts the reading and forwards it to the cloud over plain HTTP.
If the gateway returns 401 or 404, the device automatically redoes the handshake.
Gaps left in on purpose

These are your improvement targets, and also good material for the LLM-review table:

Gateway is not authenticated: the handshake is open to an active man-in-the-middle attack.
No replay protection: sessions never expire and are kept in memory only.
Plaintext gateway→cloud hop: an intentional limitation to document.
No tests, CI/CD, metrics or structured logs.
Container hygiene: containers run as root and dependencies are unpinned.
Where ML-KEM goes in

You only need to touch three places:

common/kex_legacy.py: add a hybrid function (ML-KEM-768 secret ‖ X25519 secret into HKDF).
gateway.handshake(): add a protocol_version field, and keep the v1 path behind an ALLOW_LEGACY flag.
device.handshake(): do the v2 flow, with fallback to v1.
Difference from your repo

Your repo uses MQTT (EMQX) between sensors and gateway. I used plain HTTP so the handshake is a simple request/response and the code stays small. If you want to keep MQTT, the same crypto module works unchanged. Only the transport in device.py and gateway.py would change. I’d start with this HTTP version and port it later if there’s time.
