"""Unit tests for the legacy key establishment and AEAD helpers."""
import pytest
from cryptography.exceptions import InvalidTag

from common import kex_legacy as kex


def test_keypair_public_key_is_32_bytes():
    _, pub = kex.generate_keypair()
    assert len(pub) == 32


def test_keypairs_are_ephemeral():
    _, pub1 = kex.generate_keypair()
    _, pub2 = kex.generate_keypair()
    assert pub1 != pub2


def test_both_sides_derive_the_same_32_byte_key():
    a, apub = kex.generate_keypair()
    b, bpub = kex.generate_keypair()
    ka = kex.derive_session_key(a, bpub, "dev-1")
    kb = kex.derive_session_key(b, apub, "dev-1")
    assert ka == kb
    assert len(ka) == 32


def test_device_id_is_bound_into_the_key():
    a, apub = kex.generate_keypair()
    b, bpub = kex.generate_keypair()
    assert kex.derive_session_key(a, bpub, "dev-1") != kex.derive_session_key(a, bpub, "dev-2")


def test_different_sessions_give_different_keys():
    a1, _ = kex.generate_keypair()
    a2, _ = kex.generate_keypair()
    _, bpub = kex.generate_keypair()
    assert kex.derive_session_key(a1, bpub, "d") != kex.derive_session_key(a2, bpub, "d")


def test_invalid_peer_public_key_length_is_rejected():
    a, _ = kex.generate_keypair()
    with pytest.raises(ValueError):
        kex.derive_session_key(a, b"short", "d")


def test_encrypt_decrypt_roundtrip():
    key = b"k" * 32
    nonce, ct = kex.encrypt(key, b"hello", b"aad")
    assert kex.decrypt(key, nonce, ct, b"aad") == b"hello"
    assert b"hello" not in ct


def test_nonce_is_12_bytes_and_never_repeats():
    key = b"k" * 32
    nonces = {kex.encrypt(key, b"x", b"a")[0] for _ in range(500)}
    assert len(nonces) == 500
    assert all(len(n) == 12 for n in nonces)


def test_same_plaintext_gives_different_ciphertexts():
    key = b"k" * 32
    assert kex.encrypt(key, b"same", b"a")[1] != kex.encrypt(key, b"same", b"a")[1]


def test_tampered_ciphertext_is_rejected():
    key = b"k" * 32
    nonce, ct = kex.encrypt(key, b"hello", b"aad")
    bad = bytes([ct[0] ^ 1]) + ct[1:]
    with pytest.raises(InvalidTag):
        kex.decrypt(key, nonce, bad, b"aad")


def test_tampered_tag_is_rejected():
    key = b"k" * 32
    nonce, ct = kex.encrypt(key, b"hello", b"aad")
    bad = ct[:-1] + bytes([ct[-1] ^ 1])
    with pytest.raises(InvalidTag):
        kex.decrypt(key, nonce, bad, b"aad")


def test_wrong_aad_is_rejected():
    key = b"k" * 32
    nonce, ct = kex.encrypt(key, b"hello", b"device-A")
    with pytest.raises(InvalidTag):
        kex.decrypt(key, nonce, ct, b"device-B")


def test_wrong_key_is_rejected():
    nonce, ct = kex.encrypt(b"k" * 32, b"hello", b"aad")
    with pytest.raises(InvalidTag):
        kex.decrypt(b"j" * 32, nonce, ct, b"aad")


def test_wrong_nonce_is_rejected():
    key = b"k" * 32
    nonce, ct = kex.encrypt(key, b"hello", b"aad")
    with pytest.raises(InvalidTag):
        kex.decrypt(key, bytes(12), ct, b"aad")
