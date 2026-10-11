"""Tests for the hybrid ML-KEM-768 + X25519 key exchange."""
import pytest
from cryptography.exceptions import InvalidTag

from common import kex_mlkem as kex


def establish(device_id="device-1"):
    kem_secret, kem_public, x_private, x_public = kex.generate_keypair()
    gateway_key, kem_ct, gateway_x_public = kex.encapsulate(
        kem_public, x_public, device_id
    )
    device_key = kex.decapsulate(
        kem_secret, kem_ct, x_private, gateway_x_public, device_id
    )
    return device_key, gateway_key, kem_ct


def test_mlkem_keypair_has_mlkem_768_sizes():
    secret, public, _, x_public = kex.generate_keypair()
    assert len(secret) == kex.KEM_SECRET_KEY_BYTES
    assert len(public) == kex.KEM_PUBLIC_KEY_BYTES
    assert len(x_public) == kex.X25519_PUBLIC_KEY_BYTES


def test_both_sides_derive_the_same_hybrid_key():
    device_key, gateway_key, _ = establish()
    assert device_key == gateway_key
    assert len(device_key) == 32


def test_device_id_is_bound_into_the_hybrid_key():
    secret, public, x_private, x_public = kex.generate_keypair()
    _, ciphertext, gateway_x_public = kex.encapsulate(public, x_public, "device-1")
    assert kex.decapsulate(
        secret, ciphertext, x_private, gateway_x_public, "device-1"
    ) != kex.decapsulate(secret, ciphertext, x_private, gateway_x_public, "device-2")


def test_each_encapsulation_creates_a_new_shared_key():
    first, _, _ = establish()
    second, _, _ = establish()
    assert first != second


@pytest.mark.parametrize(
    "kem_public,x_public",
    [(b"short", b"x" * 32), (b"x" * kex.KEM_PUBLIC_KEY_BYTES, b"short")],
)
def test_invalid_public_key_lengths_are_rejected(kem_public, x_public):
    with pytest.raises(ValueError):
        kex.encapsulate(kem_public, x_public, "device-1")


def test_tampered_kem_ciphertext_does_not_produce_the_original_key():
    secret, public, x_private, x_public = kex.generate_keypair()
    gateway_key, ciphertext, gateway_x_public = kex.encapsulate(public, x_public, "d")
    tampered = bytes([ciphertext[0] ^ 1]) + ciphertext[1:]
    device_key = kex.decapsulate(secret, tampered, x_private, gateway_x_public, "d")
    assert device_key != gateway_key


def test_aead_rejects_tampering():
    key, _, _ = establish()
    nonce, ciphertext = kex.encrypt(key, b"telemetry", b"device-1")
    with pytest.raises(InvalidTag):
        kex.decrypt(key, nonce, ciphertext[:-1] + bytes([ciphertext[-1] ^ 1]), b"device-1")
