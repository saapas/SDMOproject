# Raw LLM output: L01

The landing page only shows the top-level layout, so I’ll look inside the key folders.

I could only read the repo’s top level and docker-compose.yml. GitHub blocked me from opening the folders, so I haven’t seen your actual code. Here is what the compose file shows and how it maps to the assignment.

Architecture I can see

Sensors (3 containers) → MQTT broker (EMQX) → gateway-01 → cloud-api (HTTP, port 8000) → spark, which reads from a shared ./data volume. There is also an autoscaler.py and a 500-sensor load test.

What you can reuse directly
Your repo	Assignment requirement
Simulated sensors (devices/)	The simulated legacy device
gateway/	The edge gateway
cloud/	The cloud service
docker-compose.yml	Test environment and deployment target. This is a head start on the ops part.
run_load.py	Handshake and latency benchmarks, plus a realistic scale test
Git history (26 commits)	Evidence of baseline work
Suggested ML-KEM path

You have two candidates:

Gateway → cloud (HTTP). This is the easier one. The handshake is a simple request/response: POST /handshake returns the public key, the client replies with the ciphertext, and both sides derive an AES-GCM key. Only one client is involved.
Sensor → gateway (over MQTT). This fits the “legacy device migration” story better, because sensors are the constrained devices. It is harder, though. The broker sits in the middle, so you need payload-level encryption and an asynchronous handshake over topics (for example gateway/pubkey and device/<id>/kem).

With limited time, I’d do path 1 first. Add path 2 only if you have time left, or describe it as future work.

What’s missing and where the work is
CI/CD: there is no workflow visible, so you need to build it from scratch.
Tests: I saw none at the top level.
Monitoring: there are no health checks in the compose file, and I saw no metrics endpoint.
emqx/emqx:latest: the image is unpinned. This is a good example of a finding to put in your LLM-review table.
Ports 1883 and 18083 are exposed, and the broker is probably unauthenticated and plaintext. Note this as a known risk.
version: "3.9" is obsolete in current Compose.
Dockerfiles: check whether they run as root and whether the base images are pinned.
Things to watch
Spark and the autoscaler are outside the assignment’s scope. Don’t spend time on them. Keep them running if they work, or drop them from the PQ pipeline.
Course rules: the assignment says each group gets a small starting system. Check with your instructor that using your own distributed-systems project is allowed.

If you paste the contents of gateway/ and cloud/ (the main files and Dockerfiles), I can give a concrete plan for where the handshake code goes and what to baseline first.
