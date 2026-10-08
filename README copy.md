# Legacy edge-cloud baseline (pre-PQC)

device --(X25519 + AES-256-GCM over HTTP)--> gateway --(plain HTTP)--> cloud (SQLite)

Run:  docker compose up --build
Check: curl localhost:8000/readings   |   curl localhost:8080/health

Key code to replace with ML-KEM: common/kex_legacy.py (+ /handshake in gateway, handshake() in device).

Known gaps (intentional, for the assignment):
- no tests, no CI/CD, no metrics/structured logs
- no authentication of the gateway -> handshake is vulnerable to active MITM
- no replay protection, sessions never expire, sessions held in memory only
- gateway -> cloud hop is plaintext HTTP
- containers run as root, unpinned dependencies
