Implemented ML-KEM-768 hybrid key exchange.

Changes made
Added hybrid ML-KEM-768 + X25519 implementation in common/kex_mlkem.py.
Updated the device to use the hybrid handshake by default in device/device.py.
Updated the gateway to support:
Hybrid ML-KEM-768 + X25519 handshakes.
Existing legacy X25519 handshakes for migration compatibility.
Added pinned pqcrypto==0.3.4 dependencies to:
gateway/requirements.txt
device/requirements.txt
bench/requirements.txt
Added ML-KEM tests in tests/test_kex_mlkem.py.
Updated usage notes in README.md.
Added a report-ready test-results table to docs/project-report.md.
Test results
Check	Result
ML-KEM helper and hybrid derivation tests	8 passed
Legacy cryptography tests	14 passed
Gateway API and compatibility tests	27 passed, 2 expected failures
Device and end-to-end pipeline tests	6 passed
Full regression suite	68 passed, 2 expected failures
Overall coverage	98%
Ruff static analysis	Passed
The two expected failures are the existing legacy tests for replay protection and unbounded session storage.
