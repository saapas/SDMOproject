"""Legacy key establishment: ephemeral X25519 ECDH -> HKDF-SHA256 -> AES-256-GCM.

This is the module you will later replace/extend with ML-KEM (hybrid).
"""
import os

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric.x25519 import (
    X25519PrivateKey,
    X25519PublicKey,
)
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

SUITE = "legacy-x25519-aesgcm"


def generate_keypair():
    """Return (private_key_object, public_key_raw_bytes)."""
    priv = X25519PrivateKey.generate()
    pub = priv.public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw
    )
    return priv, pub


def derive_session_key(priv, peer_pub_raw: bytes, device_id: str) -> bytes:
    """ECDH + HKDF. Returns a 32-byte AES-256 key."""
    shared = priv.exchange(X25519PublicKey.from_public_bytes(peer_pub_raw))
    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=f"{SUITE}|{device_id}".encode(),
    ).derive(shared)


def encrypt(key: bytes, plaintext: bytes, aad: bytes):
    """Return (nonce, ciphertext). Fresh random 96-bit nonce per message."""
    nonce = os.urandom(12)
    return nonce, AESGCM(key).encrypt(nonce, plaintext, aad)


def decrypt(key: bytes, nonce: bytes, ciphertext: bytes, aad: bytes) -> bytes:
    """Raises cryptography.exceptions.InvalidTag on failure."""
    return AESGCM(key).decrypt(nonce, ciphertext, aad)
