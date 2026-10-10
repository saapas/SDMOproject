"""Cloud service: stores readings in SQLite and exposes them over HTTP."""
import os
import sqlite3

from fastapi import FastAPI
from pydantic import BaseModel

DB_PATH = os.getenv("DB_PATH", "/data/readings.db")
app = FastAPI(title="legacy-cloud")


def db():
    os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
    return sqlite3.connect(DB_PATH)


_c = db()
with _c:
    _c.execute(
        """CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT, gateway_id TEXT, type TEXT, value REAL, ts REAL)"""
    )
_c.close()


class Reading(BaseModel):
    device_id: str
    gateway_id: str = "unknown"
    type: str
    value: float
    ts: float


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/readings", status_code=201)
def add_reading(r: Reading):
    conn = db()
    with conn:
        conn.execute(
            "INSERT INTO readings (device_id, gateway_id, type, value, ts) VALUES (?,?,?,?,?)",
            (r.device_id, r.gateway_id, r.type, r.value, r.ts),
        )
    conn.close()
    return {"status": "stored"}


@app.get("/readings")
def list_readings(limit: int = 50):
    conn = db()
    rows = conn.execute(
        "SELECT device_id, gateway_id, type, value, ts FROM readings ORDER BY id DESC LIMIT ?",
        (min(limit, 1000),),
    ).fetchall()
    conn.close()
    return [dict(zip(("device_id", "gateway_id", "type", "value", "ts"), r, strict=True)) for r in rows]
