"""Edge gateway: terminates the device session, decrypts, forwards plaintext to the cloud."""
import base64
import json
import os
import uuid

import requests
from cryptography.exceptions import InvalidTag
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from common import kex_legacy as kex

CLOUD_URL = os.getenv("CLOUD_URL", "http://localhost:8000")
GATEWAY_ID = os.getenv("GATEWAY_ID", "gateway-01")

app = FastAPI(title="legacy-gateway")
sessions: dict[str, dict] = {}  # session_id -> {"key": bytes, "device_id": str}

b64 = lambda b: base64.b64encode(b).decode()
unb64 = base64.b64decode


class HandshakeReq(BaseModel):
    device_id: str
    client_pub: str


class TelemetryReq(BaseModel):
    session_id: str
    nonce: str
    ciphertext: str


@app.get("/health")
def health():
    return {"status": "ok", "gateway": GATEWAY_ID, "sessions": len(sessions)}


@app.post("/handshake")
def handshake(req: HandshakeReq):
    try:
        client_pub = unb64(req.client_pub)
        if len(client_pub) != 32:
            raise ValueError("bad key length")
        priv, pub = kex.generate_keypair()
        key = kex.derive_session_key(priv, client_pub, req.device_id)
    except Exception:
        raise HTTPException(400, "invalid handshake") from None
    session_id = uuid.uuid4().hex
    sessions[session_id] = {"key": key, "device_id": req.device_id}
    return {"session_id": session_id, "server_pub": b64(pub), "suite": kex.SUITE}


@app.post("/telemetry", status_code=202)
def telemetry(req: TelemetryReq):
    s = sessions.get(req.session_id)
    if s is None:
        raise HTTPException(404, "unknown session")
    try:
        plain = kex.decrypt(s["key"], unb64(req.nonce), unb64(req.ciphertext), s["device_id"].encode())
        reading = json.loads(plain)
    except (InvalidTag, ValueError):
        raise HTTPException(401, "decryption failed") from None

    reading["gateway_id"] = GATEWAY_ID
    try:
        # Gateway -> cloud hop is plain HTTP (known limitation for the legacy baseline).
        requests.post(f"{CLOUD_URL}/readings", json=reading, timeout=5).raise_for_status()
    except requests.RequestException:
        raise HTTPException(502, "cloud unreachable") from None
    return {"status": "forwarded"}
