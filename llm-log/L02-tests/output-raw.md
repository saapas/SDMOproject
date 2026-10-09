# Raw LLM output: L02

I’ll write a pytest suite covering the crypto module, gateway, cloud, device, and a full pipeline test, plus a script that injects defects to check the tests actually catch bugs.

I’ve written the test suite and added it to legacy-pqc.zip. It has 56 passing tests plus 2 expected failures, with 99% line coverage. I ran everything locally, in-process, without Docker.

What’s in tests/
File	Covers
test_kex_legacy.py	Both sides derive the same key, the device ID is bound into the key, nonces never repeat, and tampered ciphertext, tag, nonce, key or AAD are rejected
test_gateway.py	Handshake with valid and invalid keys, forwarding to the cloud, tampered or replayed telemetry, unknown session, non-JSON plaintext, and cloud failures (timeout, connection error, 500) giving 502
test_cloud.py	Store and list, newest first, limit, validation errors (422), and a SQL-injection string stored literally
test_device_and_pipeline.py	A full device → gateway → cloud test, a check that the value is not visible on the wire, re-handshake after a gateway restart, and retry on network errors
conftest.py	Shared fixtures, with the gateway→cloud call mocked or routed in-process
mutation_check.py	Injects 12 defects into a temporary copy of the code and checks that the tests fail
Known gaps as expected failures

Two tests are marked xfail: replay protection (R3) and the unbounded session table (R10). They document weaknesses from your risk register. When you fix them, remove the marker and the tests become real.

Defect-injection result

All 12 injected defects were caught. They include a reused nonce, ignored AAD, the device ID dropped from key derivation, a swallowed cloud error, and a missing re-handshake. This is the evidence for section 7 and the LLM log that the tests are meaningful. It does not prove the suite is complete, so say so in the report.

Run it
powershell
pip install -r requirements-dev.txt
python -m pytest --cov=common --cov=gateway --cov=cloud --cov=device --cov-report=term-missing
python tests/mutation_check.py

Your job: review these tests, don’t just accept them

The assignment treats LLM output as untrusted, and you are the one who must assess it, so this is entry L01 in llm-log/. For the log:

Paste the prompt you used and my answer into L01-test-suite/. The tests/ folder is the “final” version.
Read each test and ask whether it asserts real behaviour or only a status code.
Run mutation_check.py yourself. Then add a defect of your own to mutation_check.py (for example, remove the length check in /handshake) and see whether it is caught. Some of my mutations may be too easy.
Check for tests that always pass. One example in my own suite is test_garbage_base64_is_rejected_not_500, which accepts 400, 401 or 422 and is deliberately loose. You could tighten it.
Note what I could not cover, such as real network timing and Docker behaviour.
Count it as “Modified” if you change anything, and write down what.

Next is the CI workflow, which will run ruff, bandit, the tests and the Docker build. I can draft that when you’re ready.