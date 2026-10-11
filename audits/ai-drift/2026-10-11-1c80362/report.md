# AI drift audit — SDMOproject @ 1c80362 (2026-10-11)

> Produced by the `ai-drift-audit` skill (first test run, Claude Opus 5.5 sub-agent). Text below is
> the agent's output unchanged, except the final section, which is replaced by "Reviewer notes"
> (verification and one finding the run missed). See `llm-log/L06-ai-drift-audit/`.

**Scope:**
- LLM logs: every file in `llm-log/` at HEAD (L01 `output-raw.md`, `output2-raw.md`, `output3-raw.md`; L02, L03 `output-raw.md` + `output2-raw.md`; L04; L05 (empty template); all `entry*.md`; `llm-log/README.md`), plus the earlier version of `llm-log/L01-legacy-system/output-raw.md` that was replaced in commit `d362548`. That earlier version is the source of several terms used in the documents.
- Repository docs: `README.md`, `docs/architecture.md`, `docs/risk-register.md`, `docs/*-results.md`.
- External documents: `~/Downloads/Project Report Group 19.pdf` (5 pages) and `~/Downloads/Technical Documentation.pdf` (5 pages), text extracted with pypdf.
- Code read: `common/kex_legacy.py`, `common/kex_mlkem.py`, `gateway/gateway.py`, `device/device.py`, `cloud/cloud.py`, all `tests/*.py`, `scripts/smoke_test.py`, `.github/workflows/ci.yml` and `mutation.yml`, `docker-compose.yml`, all Dockerfiles and `requirements*.txt`; git history of all 47 commits on all branches; tag `baseline-legacy`.

**Method:** ai-drift-audit skill; helper `locate.py`; code read for every finding. Nothing in the project was run.

## Summary
| Category | Findings |
|---|---|
| A. Recommended → documented → not implemented | 5 |
| B. Claimed done → does not exist | 2 |
| C. To-do → neither done nor recorded | 4 (+1 added in review) |
| D. Reverse drift (implemented, docs outdated) | 5 |

The hybrid ML-KEM-768 + X25519 handshake is implemented and is the device default. But the migration-control layer the report describes around it does not exist in code: there is no `ALLOW_LEGACY` setting, no `protocol_version` field, no version or transcript binding beyond the suite name, no downgrade test, and no migration metrics or logs. A reader of the report would believe legacy clients can be switched off, that downgrade resistance is tested, and that operators can watch migration progress. In reality the gateway accepts legacy X25519 clients unconditionally and silently. In the other direction, the technical documentation and README still describe ML-KEM, tests, CI and container hardening as missing, though they all exist.

## Findings

### A1. `ALLOW_LEGACY` migration setting does not exist — Confirmed
- **LLM said:** "keep the v1 path behind an ALLOW_LEGACY flag." — `llm-log/L01-legacy-system/output3-raw.md:37`; earlier L01 raw output: "Add a config flag ALLOW_LEGACY=true/false so you can show a migration plan (phase 1: allow both and log legacy use; phase 2: warn; phase 3: reject legacy)" — `git show 1793546:llm-log/L01-legacy-system/output-raw.md` line 22
- **Documented as:**
  - "Legacy clients are controlled by the 'ALLOW_LEGACY' migration setting." — report §2, p.2
  - "It uses the setting 'ALLOW_LEGACY' so the old protocol can be turned off after the migration is done." — report §3.5, p.4
  - "that is why we needed to implement … the 'ALLOW_LEGACY' setting" — report §4, p.4
  - Phase table "1: Dual support … ALLOW_LEGACY=true", "3: PQ only, Reject v1, ALLOW_LEGACY=false" — technical documentation §3, p.2
- **Code:** `gateway/gateway.py` reads only `CLOUD_URL` and `GATEWAY_ID` (lines 15–16). The legacy branch `elif req.client_pub:` (lines 66–72) runs for any request with a `client_pub`, with no condition, no warning and no log line.
  - Evidence: `locate.py ALLOW_LEGACY` → code 0 / tests 0 at HEAD, 0 commits.
  - Evidence: `git grep -n -E "ALLOW_LEGACY|getenv" HEAD -- gateway device common` → only the six unrelated env vars.
- **History:** never in code or tests in any of 47 commits
- **Suggested action:** implement `ALLOW_LEGACY` (an env var read in `gateway.py`; reject `client_pub` handshakes with 4xx when false; add a test for both settings). Or change report §2, §3.5, §4 and technical documentation §3 to describe it as planned work.

### A2. No `protocol_version` field in the handshake — Confirmed
- **LLM said:** "with a protocol version field so legacy devices keep working during migration" — `llm-log/L01-legacy-system/output-raw.md:48`; "gateway.handshake(): add a protocol_version field" — `llm-log/L01-legacy-system/output3-raw.md:37`
- **Documented as:** "Legacy devices keep working through a protocol_version field and the ALLOW_LEGACY flag." — technical documentation §3 "Migration and fallback", p.2; "Our implementation binds the protocol version and suite to the KDF context" — report §3.5, p.4
- **Code:** `HandshakeReq` (`gateway/gateway.py:25–29`) has only `device_id`, `client_pub`, `kem_public_key` and `x25519_public_key`. The suite is chosen implicitly by which key fields are present (`gateway.py:55`, `:66`). The device sends no version (`device/device.py:25–29`). Evidence: `locate.py protocol_version` → code 0 / tests 0, 0 commits.
- **History:** never in code in 47 commits
- **Suggested action:** add an explicit version field, or change the docs to say that the suite is selected by the presence of the ML-KEM key fields.

### A3. Protocol version / handshake transcript not bound into the KDF; no downgrade test — Confirmed
- **LLM said:** "Downgrade protection: include the version in the HKDF context so an attacker can't silently force v1." — `git show 1793546:llm-log/L01-legacy-system/output-raw.md` line 23. This is also the team's own plan in `docs/risk-register.md:15`, R11: "Include version/suite in HKDF context + transcript".
- **Documented as:**
  - "Our implementation binds the protocol version and suite to the KDF context and handshake. … Our testing makes sure that a hybrid client can not be silently downgraded by changing the suite or version." — report §3.5, p.4
  - "binds the protocol version, device ID and suite to it" — report §5, p.5
  - "device ID and suite are included in the key derivation", presented as a tested property — report §3.4, p.3
- **Code:** HKDF uses `info=f"{SUITE}|{device_id}"` (`common/kex_mlkem.py:79`, `common/kex_legacy.py:34`).
  - The suite and device ID are bound; that part of the claim is true.
  - There is no version to bind (see A2), and no transcript (public keys, KEM ciphertext) in `info`.
  - No test varies the suite or attempts a downgrade. The only binding tests are for device ID (`tests/test_kex_mlkem.py:32`, `tests/test_kex_legacy.py:28`).
  - Evidence: `git grep -n -i downgrade $(git log --all --format=%h) -- tests` → none in any commit.
- **History:** never in code or tests in 47 commits. R11 in the risk register still says "Version not bound into key derivation yet", so the in-repo register is accurate and the report is not.
- **Note:** the current device has no legacy path, so in practice a hybrid device cannot be downgraded: a stripped response makes `device.handshake()` fail on `body["kem_ciphertext"]`. That protection comes from the missing fallback, not from KDF binding, and no test checks it.
- **Suggested action:** add a downgrade test and transcript binding. Or reword report §3.4, §3.5 and §5: the suite and device ID are bound; version/transcript binding and downgrade tests are open work (R11).

### A4. Device-side "fallback to v1" / "controlled legacy fallback" not implemented — Likely
- **LLM said:** "device.handshake(): do the v2 flow, with fallback to v1." — `llm-log/L01-legacy-system/output3-raw.md:38`
- **Documented as:** "… with a legacy fallback" — technical documentation §1, p.1; "The final version supports a controlled legacy fallback" — report §5, p.5
- **Code:** `device/device.py:21–42` does the hybrid handshake only. On error, `main()` retries the hybrid handshake (`:70–78`). The gateway does accept legacy clients (`gateway/gateway.py:66–72`), but with no control (see A1). Evidence: `locate.py fallback` → code 0, 0 commits.
- **Why "Likely":** "legacy fallback" may just mean that the gateway accepts legacy clients, which is true. "Controlled" depends on A1.
- **Suggested action:** say that compatibility exists on the gateway only and is uncontrolled, or implement the device fallback and A1.

### A5. Migration metrics and structured logging do not exist — Confirmed
- **LLM said:**
  - "Monitoring: /health endpoints, structured JSON logs and Prometheus metrics, including handshake counts per suite."
  - "The metric that shows migration progress is the ratio of legacy to post-quantum handshakes." — both `llm-log/L01-legacy-system/output-raw.md:47,50`
  - The earlier L01 raw output listed `handshakes_total{suite=…}`, `handshake_failures_total`, `handshake_duration_seconds` and `legacy_clients_active` — `git show 1793546:llm-log/L01-legacy-system/output-raw.md` lines 38–45
- **Documented as:**
  - Technical documentation §6, p.3–4, lists `handshakes_total{suite}` ("PQ vs legacy migration progress"), `handshake_failures_total{reason}`, `handshake_duration_seconds` and `legacy_clients_active`.
  - Technical documentation §3: "log legacy use", "Warn on every legacy handshake".
  - "Metrics and logs show hybrid and legacy handshakes and failures, as well as the migration process." — report §2, p.2
  - "adding the necessary tests, metrics, and CI support" — report §1
  - "reports migration process" — report §5
- **Code:**
  - The only routes are `/health`, `/handshake`, `/telemetry` (gateway) and `/health`, `/readings` (cloud).
  - The gateway has no logging and no print at all. `/health` returns only a session count (`gateway.py:47–49`).
  - No metrics library appears in any requirements file. The device uses plain `print`.
  - Evidence: `locate.py handshakes_total … /metrics prometheus` → code 0, 0 commits for each.
  - Evidence: `git grep -i -E "metrics|prometheus|logging|logger" HEAD -- gateway device cloud common "*/requirements.txt"` → none.
- **History:** never in code in 47 commits. `llm-log/L05-metrics-logging/` is an unfilled template with an empty output. Risk register R8 and the README "Known gaps" correctly list this as open.
- **Suggested action:** implement `/metrics` with at least `handshakes_total{suite}` and log legacy handshakes. Or mark technical documentation §6 as planned and remove the claims from report §1, §2 and §5.

### B1. "Report-ready test-results table in docs/project-report.md" never created — Confirmed
- **LLM said:** "Added a report-ready test-results table to docs/project-report.md." — `llm-log/L04-mlkem-integration/output-raw.md:15`
- **Documented as:** "The report-ready comparison is in `docs/project-report.md`." — `README.md:122–123` (added in `8a29a42`)
- **Code:** the file does not exist. Evidence: `git log --all --oneline -- docs/project-report.md` → empty.
- **History:** never present in any of 47 commits
- **Suggested action:** fix the README pointer (to `docs/mlkem-results.md` / `docs/matched-baseline-results.md`), and note the false claim in the L04 review.

### B2. "Exact versions in every requirements.txt" is false: bench unpinned and not audited — Confirmed
- **LLM said:** "Pinned dependencies: exact versions in every requirements.txt, plus a pinned requirements-dev.txt." — `llm-log/L03-ci-workflow/output2-raw.md:51`; "pip-audit on each requirements file" — `:16`
- **Documented as:** not repeated in the PDFs. The L03 entries mark the output "Modified" without noting this.
- **Code:**
  - `bench/requirements.txt` had `requests>=2.31`, `cryptography>=42` when the L03 changes landed (`git show 3f76ac0:bench/requirements.txt`) and still does at HEAD.
  - `ci.yml:42–43` runs pip-audit only on `device`, `gateway` and `cloud`, so `bench` and `requirements-dev.txt` are never audited.
  - `cryptography>=42` still allows 46.0.6, the version the same LLM output says has 9 known vulnerabilities.
- **History:** unpinned since `ab42fd5`
- **Suggested action:** pin `bench/requirements.txt` and add it to the pip-audit loop, or record it as an exception under R9.

### C1. Base image not pinned by digest; not recorded — Confirmed
- **LLM said:** "Pin the base image by digest (python:3.12-slim@sha256:...)." — `llm-log/L03-ci-workflow/output2-raw.md:53`
- **Documented as:** nowhere (R9 says only "Harden Dockerfiles")
- **Code:** `FROM python:3.12-slim` in all three Dockerfiles, line 2. Evidence: `locate.py sha256:` → code 0, 0 commits.
- **Suggested action:** pin the digest, or add it to the risk register.

### C2. Actions pinned to major tags, not SHAs; not recorded — Confirmed
- **LLM said:** "the Actions are pinned to major versions (@v4, @v5). Commit SHAs are stricter, so mention this as remaining hardening." — `llm-log/L03-ci-workflow/output2-raw.md:53`
- **Documented as:** nowhere
- **Code:** `ci.yml:19,20,31,32,49,50,61,70` and `mutation.yml:16,17,24` use `@v4` / `@v5`
- **Suggested action:** pin to SHAs, or record it in the risk register.

### C3. CI differs from the accepted L03 plan; deviation not recorded — Confirmed
- **LLM said:** "Run on every push and pull request. Run the deploy job only on main." and "upload the coverage report and the smoke-test logs." — `llm-log/L03-ci-workflow/output-raw.md:17,23`. The L03 entry decision was Accepted.
- **Code:**
  - `ci.yml:3–6` triggers on pushes to `main` plus all PRs, so pushes to other branches are not checked.
  - `build-and-smoke-test` (`:66–82`) has no branch `if:`, so the deploy runs on every PR.
  - Only `coverage.xml` is uploaded. Logs are printed on failure (`:77–79`) but not kept as an artifact.
- **Suggested action:** restrict the deploy job to main and upload the smoke logs, or note the deviation in L03.

### C4. No recorded evidence that the pipeline blocks bad code — Needs human check
- **LLM said:** "Prove the pipeline blocks bad code. Push one commit that breaks a test, and one with a ruff error, and save the failing runs as evidence for section 5." — `llm-log/L03-ci-workflow/output2-raw.md:55`
- **Documented as:** technical documentation §5 links no failing run. The L03 verification is only a local ruff result (`entry2.md:24`).
- **Evidence:** Actions history is not in the repo.
- **Suggested action:** check GitHub Actions and link a failing run in §5, or record this as open.

### D1. README "Known gaps" still lists tests, CI/CD, root containers and unpinned deps — Confirmed
- **Documented as:** `README.md:13–18`; also the title "(pre-PQC)" and the diagram at `:1–3`
- **Code:**
  - The tests, `.github/workflows/ci.yml`, `USER app` in all Dockerfiles, exact pins in cloud/device/gateway, and the hybrid default (`device/device.py:10`) all exist.
  - The README contradicts itself: `:8–11` and `:126–129` describe ML-KEM and the tests.
- **History:** the text dates from `ab42fd5`. Later changes: tests `43a90ce`, CI and hardening `3f76ac0`, ML-KEM `1ac7de3`.
- **Suggested action:** label the list as the baseline-tag gaps, or update it to the remaining gaps.

### D2. Technical documentation §7 says ML-KEM / v2 does not exist yet — Confirmed
- **Documented as:** "Handshake roundtrip (v1 and v2) — partly — We don't have the ML-KEM yet"; "Downgrade attempt rejected — Not yet — No v2 yet"; "Coverage: 99%" — p.4
- **Code:**
  - `common/kex_mlkem.py` and `tests/test_kex_mlkem.py` (8 tests, roundtrip at `:26`) exist since `1ac7de3`.
  - The hybrid handshake through the gateway is tested in `tests/test_device_and_pipeline.py:15`.
  - L04 reports 98% coverage.
  - The downgrade row is still correct in substance (A3), but the stated reason is outdated.
- **Suggested action:** update §7.

### D3. Technical documentation §1–§3 still has placeholders and names the wrong library — Confirmed
- **Documented as:** "Library: [liboqs-python / other]" (§3); hybrid measurements "[ ]" (§2); "Main results: […]" and "Final tag: [tag]" (§1)
- **Code:**
  - The project uses `pqcrypto==0.3.4` (`common/kex_mlkem.py:11–13`, `gateway/requirements.txt:4`, `device/requirements.txt:2`). liboqs was the LLM's suggestion: L01 `output-raw.md:48`, L03 `output2-raw.md:58`.
  - Hybrid numbers exist in `docs/mlkem-results.md` and in report §3.4.
  - The only tag is `baseline-legacy`.
- **Suggested action:** fill in §1–§3.

### D4. LLM-log documentation does not reflect L04 — Confirmed
- **Documented as:**
  - Technical documentation §8: "Claude Sonnet 5.5 Medium", and the ML-KEM row "[link] [ ] [ ] [ ]".
  - `llm-log/README.md:6,13–17`: "Claude Sonnet 5.5", with "[ ]" in every decision cell.
- **Log:** `llm-log/L04-mlkem-integration/entry.md:3` says "GPT 5.6 Luna", decision Accepted. The L01–L03 decisions are not mirrored in the index either. The L04 entry is headed "# L01: Legacy system", a copy-paste leftover.
- **Suggested action:** list both models and fill the rows. Record the false B1 claim in the L04 review.

### D5. Risk register does not mark implemented mitigations R1, R7, R9 — Confirmed
- **Documented as:** `docs/risk-register.md:5,11,13` still show R1, R7 and R9 as planned. Only R6 is marked MITIGATED. Report §2 calls the register "the full risk list of the current project state".
- **Code:** R1 done in `1ac7de3`, R7 in `3f76ac0`, R9 mostly in `3f76ac0`. What remains of R9 is B2, C1 and C2.
- **Suggested action:** add a status column.

## Checked and consistent
- **Hybrid handshake:** implemented in `common/kex_mlkem.py`. HKDF runs over `kem_shared + x25519_shared` (`:74–80`). The device uses it by default and the gateway supports both suites (`gateway.py:55–72`). This matches report §2 and §3.3 and the L04 claims.
- **L04 file claims:** all present except B1. The test counts match the test definitions: 14 + 8 + 27 (+2 xfail) + 6 + 13 = 68 + 2. Not re-run.
- **L03 claims:**
  - CI has the four jobs: lint (ruff), security (bandit `-ll` and pip-audit), tests (coverage gate 90), and build-and-smoke-test (`--wait-timeout 120`, smoke test, logs on failure, `down -v`).
  - `mutation.yml` runs manually and weekly.
  - Containers run as non-root uid 10001.
  - Compose has healthchecks and `service_healthy` dependencies; the cloud uses the `cloud-data` volume.
  - `cryptography==50.0.1`; the `from None`, `strict=True` and `nosec B311` code edits are in place.
  - Technical documentation §5 matches `scripts/smoke_test.py`.
- **L02 claims:**
  - The test files match the description.
  - The xfail tests for R3 and R10 are at `tests/test_gateway.py:176,184`.
  - The loose test was tightened, and the suggested mutation was added (`tests/mutation_check.py:32`).
  - The README's "16 defects" matches `MUTATIONS`.
- **L01 recommendations implemented:** `/health`, API and failure-case tests, the CI stages, and the baseline benchmark with tag `baseline-legacy`.
- **Honestly documented as open:** gateway auth/MITM (R2), replay (R3), plaintext gateway→cloud (R4), session table (R10).
- **Report §3.4 tables:**
  - The legacy table equals `docs/matched-baseline-results.md`.
  - The hybrid table equals `docs/mlkem-results.md` as committed in `1ac7de3`.
  - Technical documentation §2 legacy numbers equal `docs/baseline-results.md` at `baseline-legacy`.
- **Baseline-labelled docs:** `docs/architecture.md` and technical documentation §2 (`./data` volume) describe the baseline and say so.
- **Library change:** replacing liboqs with pqcrypto is a design change, not drift (but see D3).

## Other observations (outside A–D)
- **Report numbers overwritten:** `docs/mlkem-results.md` was overwritten in `1c80362` by a Docker run. The report's hybrid numbers now exist only in history. Keep a separate "matched" file, as was done for the legacy run.
- **Mislabelled column:** technical documentation §2 says "mean / p95" but shows only the p95.
- **Replay wording:** report §2 says the tests cover "replay", but the replay test is xfail. §3.4 is accurate.
- **Gateway test claim:** report §3.4 says the gateway tests cover valid hybrid handshakes. `tests/test_gateway.py` is legacy-only. The hybrid path through the API is tested only in the pipeline test, and invalid hybrid requests only at the crypto level.

## Limits of this audit
- Nothing was executed: tests, coverage, benchmarks and the Docker build with pqcrypto were not reproduced. L03 itself said the Docker and Actions runs were unverified.
- Actions run history (C4) is not visible from the repo.
- The diagram on technical documentation p.1 could not be rendered; only the text was audited.
- The source of `ALLOW_LEGACY=true/false`, the three-phase plan and the metric names is a raw L01 output replaced in `d362548`. It is not in `llm-log/` at HEAD.
- The working tree had changes this audit did not make: a modified `llm-log/README.md` (L06 row) and an untracked `llm-log/L06-ai-drift-audit/`. These were not used as evidence.

## Reviewer notes (added by the human-reviewed session, not by the audit run)

**Verified independently** before saving this report:
- A1/A5 source: `git show 1793546:llm-log/L01-legacy-system/output-raw.md` contains the
  `ALLOW_LEGACY=true/false` three-phase plan, "include the version in the HKDF context", and the four
  metric names; that file was replaced in `d362548`.
- B1: `README.md:123` points to `docs/project-report.md` (added in `8a29a42`); `git log --all -- docs/project-report.md` is empty.
- Other observations: `git diff 1ac7de3 1c80362 -- docs/mlkem-results.md` changes the hybrid
  handshake mean from 2.229 ms (Windows, local) to 43.685 ms (Docker).
- Gateway test claim: `grep -c kem_public_key tests/test_gateway.py` → 0.

**Added finding the run missed:**

### C5. Mutation testing does not cover the ML-KEM code — Confirmed
- **LLM said:** "Then add a defect of your own to mutation_check.py … Some of my mutations may be too easy." — `llm-log/L02-tests/output-raw.md`; the L02 entry says the suggested mutations were added.
- **Documented as:** "LLM-generated tests, reviewed + mutation-checked (MITIGATED)" — `docs/risk-register.md`, R6; README "injects 16 defects into a temp copy, checks the tests catch them".
- **Code:** `tests/mutation_check.py` has 16 mutations; `grep -c kex_mlkem tests/mutation_check.py` → 0. All of them predate `common/kex_mlkem.py` (added in `1ac7de3`), so the module that the project is about has no mutation evidence.
- **Suggested action:** add mutations for `kex_mlkem.py` (e.g. drop the X25519 secret from `_derive`, skip a length check), or limit the R6 claim to the legacy code.

**Log entry:** this audit is recorded in `llm-log/L06-ai-drift-audit/`.

## Addendum: changes on `main` after the audit (checked at `0d4f648`)

Three commits landed while the audit ran (`ff46dbd`, `f06d831`, `0d4f648`). They change docs only;
`git diff --stat 1c80362 0d4f648` shows no code changes.

| Item | Change | Status now |
|---|---|---|
| D5 (risk register status) | R1 marked PARTIALLY MITIGATED, R7 and R9 marked MITIGATED | **Resolved.** R9 is partly true: B2, C1, C2 still open |
| A3 (version/transcript in KDF) | R11 marked **MITIGATED** | **Drift has spread to the risk register.** Code unchanged: `common/kex_mlkem.py:79` still binds only `suite\|device_id`; no version field, no transcript, no downgrade test |
| Report §3.4 legacy numbers | `docs/matched-baseline-results.md/.json` deleted | The report's legacy table now has no source in the repo (only in history, e.g. `git show 1c80362:docs/matched-baseline-results.md`); the hybrid table's source was overwritten earlier (see "Other observations") |
