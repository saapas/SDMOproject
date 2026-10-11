"""Hybrid ML-KEM-768 + X25519 key establishment and AES-GCM helpers."""
import os

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric.x25519 import (
    X25519PrivateKey,
    X25519PublicKey,
)
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from pqcrypto.kem.ml_kem_768 import decrypt as kem_decrypt
from pqcrypto.kem.ml_kem_768 import encrypt as kem_encrypt
from pqcrypto.kem.ml_kem_768 import generate_keypair as kem_generate_keypair

SUITE = "hybrid-ml-kem-768-x25519-aesgcm"
KEM_PUBLIC_KEY_BYTES = 1184
KEM_SECRET_KEY_BYTES = 2400
KEM_CIPHERTEXT_BYTES = 1088
X25519_PUBLIC_KEY_BYTES = 32


def generate_keypair():
    """Return a client keypair as ``(kem_secret, kem_public, x25519_private, x25519_public)``."""
    kem_public, kem_secret = kem_generate_keypair()
    x25519_private = X25519PrivateKey.generate()
    x25519_public = x25519_private.public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw
    )
    return kem_secret, kem_public, x25519_private, x25519_public


def encapsulate(peer_kem_public: bytes, peer_x25519_public: bytes, device_id: str):
    """Encapsulate to a client public key and return ``(key, kem_ct, x25519_public)``."""
    if len(peer_kem_public) != KEM_PUBLIC_KEY_BYTES:
        raise ValueError("invalid ML-KEM public key length")
    if len(peer_x25519_public) != X25519_PUBLIC_KEY_BYTES:
        raise ValueError("invalid X25519 public key length")
    kem_ciphertext, kem_shared = kem_encrypt(peer_kem_public)
    x25519_private = X25519PrivateKey.generate()
    x25519_public = x25519_private.public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw
    )
    x25519_shared = x25519_private.exchange(
        X25519PublicKey.from_public_bytes(peer_x25519_public)
    )
    return (
        _derive(kem_shared, x25519_shared, device_id),
        kem_ciphertext,
        x25519_public,
    )


def decapsulate(
    kem_secret: bytes,
    kem_ciphertext: bytes,
    x25519_private: X25519PrivateKey,
    peer_x25519_public: bytes,
    device_id: str,
) -> bytes:
    """Decapsulate the server response and derive the AES-256 session key."""
    if len(kem_secret) != KEM_SECRET_KEY_BYTES:
        raise ValueError("invalid ML-KEM secret key length")
    if len(kem_ciphertext) != KEM_CIPHERTEXT_BYTES:
        raise ValueError("invalid ML-KEM ciphertext length")
    if len(peer_x25519_public) != X25519_PUBLIC_KEY_BYTES:
        raise ValueError("invalid X25519 public key length")
    kem_shared = kem_decrypt(kem_secret, kem_ciphertext)
    x25519_shared = x25519_private.exchange(
        X25519PublicKey.from_public_bytes(peer_x25519_public)
    )
    return _derive(kem_shared, x25519_shared, device_id)


def _derive(kem_shared: bytes, x25519_shared: bytes, device_id: str) -> bytes:
    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=f"{SUITE}|{device_id}".encode(),
    ).derive(kem_shared + x25519_shared)


def encrypt(key: bytes, plaintext: bytes, aad: bytes):
    """Return ``(nonce, ciphertext)`` with a fresh random 96-bit nonce."""
    nonce = os.urandom(12)
    return nonce, AESGCM(key).encrypt(nonce, plaintext, aad)


def decrypt(key: bytes, nonce: bytes, ciphertext: bytes, aad: bytes) -> bytes:
    """Raise ``cryptography.exceptions.InvalidTag`` when authentication fails."""
    return AESGCM(key).decrypt(nonce, ciphertext, aad)
