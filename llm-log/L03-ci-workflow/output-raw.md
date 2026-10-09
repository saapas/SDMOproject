# Raw LLM output: L03

I’d keep it as one GitHub Actions workflow with a few small jobs, so a failure points at one clear stage. Your tests run in-process, so most of the pipeline doesn’t need Docker.

Pipeline
Stage	Tool	Fails the build when	Notes
1. Lint	ruff check	Any rule violation	Fast, so it runs first
2. Static security	bandit -r common device gateway cloud	Medium or high findings	Run it locally first to see what it flags
3. Dependency audit	pip-audit	Known vulnerable packages	Cheap supply-chain check, useful for the report
4. Tests	pytest --cov --cov-fail-under=90	A test fails or coverage drops	You’re at about 99 % now, so 90 leaves headroom
5. Build	docker compose build	A Dockerfile breaks	Runs after 1 to 4 pass
6. Deploy + smoke test	docker compose up -d --wait, then curl /health and /readings	A service is unhealthy or no readings arrive	This is your “deploy to a test environment”

Stages 1 to 4 can run in parallel as separate jobs. Stages 5 and 6 depend on them.

Decisions I’d make
Triggers: run on every push and pull request. Run the deploy job only on main.
Mutation check: don’t run it on every push, because it takes a few minutes. Make it a manual or weekly job (workflow_dispatch or schedule) and upload the result as an artifact.
Deploy target: the simplest version that satisfies the brief is the deploy job starting the compose stack on the GitHub runner and checking it. That makes the runner your test environment, and it needs no secrets. If your course provides a VM, a more realistic variant pushes images to GitHub Container Registry and deploys over SSH with docker compose pull. That needs repository secrets, so only do it if you have the time.
Health checks: docker compose up --wait only works if the services declare healthcheck. Your compose file has none yet. The python:slim image has no curl, so the check should use a one-line Python urllib call against /health.
Reproducibility (R9): pin dependency versions (a lock file or exact versions in requirements.txt) and pin the base image and each action version. Use a non-root user in the Dockerfiles.
Least privilege: set permissions: contents: read at the top, add no secrets unless deploying remotely, and never use || true, which hides failures.
Artifacts: upload the coverage report and the smoke-test logs.
What to review in the LLM-generated version (entry L03)

If the LLM writes the workflow, check these:

Are actions pinned to a version, or to @main or @latest?
Does any step ignore its own failure?
Are permissions too broad?
Are secrets or tokens printed or committed?
Does the smoke test check real behaviour, such as data reaching the cloud, or only that containers started?
Does a deliberately broken commit make the pipeline fail? Test that, and keep the failing run’s link as evidence for section 5.
Plan for the PQC upgrade

When liboqs arrives, the Docker build gets slower and more fragile because of the native library. Cache the image layers, and treat that build step as its own stage.

I can write the workflow, the compose healthchecks and the hardened Dockerfiles. I can test ruff, bandit, pip-audit and pytest here, but I can’t run the GitHub workflow or the Docker build, so you’d need to confirm those on your side. Shall I go ahead?
