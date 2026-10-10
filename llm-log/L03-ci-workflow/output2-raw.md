# Raw LLM output: L03

The smoke test passes against a live stack and fails correctly when the gateway is down. I’ll fix a small comment-format warning and bundle only the changed and new files.

The CI/CD pipeline is written and tested as far as I can test it here. ci-changes.zip has only the 15 new or changed files, with their paths, so you can unzip it over your repo. It does not include the whole system or your test files.

What I could and couldn’t verify
Verified here: ruff, bandit, pip-audit, pytest with the 90 % coverage gate (99 %), and all YAML files parse. I also ran scripts/smoke_test.py against a real local stack with three simulated sensors (it passed), and then with the gateway killed (it failed correctly).
Not verified: the Docker build, the compose healthchecks and the GitHub Actions run. This sandbox has no Docker, and I can’t run GitHub workflows. Check these on your side, and keep the first failing run’s log if something breaks, since that’s useful evidence.
What the pipeline does (.github/workflows/ci.yml)

Four jobs. lint, security and test run in parallel, and build-and-smoke-test runs only after all three pass.

Job	Commands
lint	ruff check .
security	bandit -ll -r common device gateway cloud scripts, then pip-audit on each requirements file
test	pytest with --cov-fail-under=90, uploads coverage.xml
build-and-smoke-test	docker compose build, up -d --wait --wait-timeout 120, then python3 scripts/smoke_test.py, logs on failure, and down -v always

The mutation check is a separate mutation.yml (manual and weekly), so it doesn’t slow every push.

Findings from running the tools

These are real findings for the L03 entry and section 5 of your documentation:

pip-audit found 9 known vulnerabilities in cryptography 46.0.6. I pinned 50.0.1 instead (the fix versions go up to 50.0.0, and I skipped 50.0.2 because it is only nine days old). The tests pass with it.
ruff found 4 real issues: three raise ... from None cases in the gateway and a zip() without strict=True in the cloud. Both are fixed.
bandit flagged random in the device. It’s simulated sensor data, so I suppressed it with a comment explaining why.
Small edits to existing code
python
# gateway/gateway.py: three raises, same change each
raise HTTPException(400, "invalid handshake") from None
raise HTTPException(401, "decryption failed") from None
raise HTTPException(502, "cloud unreachable") from None

# cloud/cloud.py
dict(zip(("device_id", "gateway_id", "type", "value", "ts"), r, strict=True))

# device/device.py
    # simulated sensor data, not used for cryptography
    return round(random.uniform(lo, hi), 2)  # nosec B311

In your own tests/test_device_and_pipeline.py, run ruff check --fix --select I tests/test_device_and_pipeline.py once. It sorts one import block that ruff complained about.

Docker and compose changes
Dockerfiles: each now creates a non-root user (app, uid 10001), sets PYTHONDONTWRITEBYTECODE, and uses pip install --no-cache-dir. The cloud one also creates /data owned by app.
docker-compose.yml:
Healthchecks on cloud and gateway use a one-line Python call, because the slim image has no curl.
Startup order is enforced: the gateway waits for a healthy cloud, and the sensors wait for a healthy gateway.
./data became a named volume (cloud-data). A bind mount would be owned by the runner’s user and the non-root container couldn’t write to it. The SQLite file is no longer in your data/ folder; use docker compose down -v to reset it.
Pinned dependencies: exact versions in every requirements.txt, plus a pinned requirements-dev.txt.
Things to do or decide
Pin the base image by digest (python:3.12-slim@sha256:...). Pull the image and read the digest, since I can’t. Likewise, the Actions are pinned to major versions (@v4, @v5). Commit SHAs are stricter, so mention this as remaining hardening.
pip-audit can fail an unchanged commit when a new vulnerability is published. That is intended, but tell the group.
Prove the pipeline blocks bad code. Push one commit that breaks a test, and one with a ruff error, and save the failing runs as evidence for section 5.
Log it as L03. Record the prompt and my answer, and write down the findings above. Also note that I wrote the workflow and tested it only partly.

When you’re ready for the PQC work, I’d start by checking that liboqs-python builds in the Docker image, because that is the most likely thing to break the CI build.