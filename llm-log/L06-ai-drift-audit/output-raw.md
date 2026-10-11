# Raw LLM output: L06

## Answer to prompt 1 ("reconfirm : No ALLOW_LEGACY anywhere.")

Confirmed, with one wording correction: `ALLOW_LEGACY` does appear in the repo, but **only in LLM log text, never in code**. "Not anywhere" was too strong; "not implemented in any code" is accurate.

What I checked, against the latest `main` (`1c80362`, the only branch):

| Where | Result |
|---|---|
| Code and config (`.py`, workflows, Dockerfiles, `docker-compose.yml`, tests) | **No match**, case-insensitive, including spellings like `allow-legacy` |
| Current files overall | **1 match**: [llm-log/L01-legacy-system/output3-raw.md:37](../SDMOproject/llm-log/L01-legacy-system/output3-raw.md), the LLM's recommendation *"keep the v1 path behind an ALLOW_LEGACY flag"* |
| Entire git history, all branches | 5 commits mention it, and all of them only edit `llm-log/L01-legacy-system/output*-raw.md`. **No commit has ever put it in code** |

Where else the text appears: the report (§2, §3.5, §4, §5) and the technical documentation (§3 migration table). Neither PDF is in the repo; both came from your message.

How the code actually behaves, from [gateway/gateway.py](../SDMOproject/gateway/gateway.py):
- `handshake()` runs the hybrid path if the client sends ML-KEM keys and the legacy X25519 path if it sends `client_pub`.
- No setting, policy or log line controls or records that choice.

So the trail is: the LLM recommended `ALLOW_LEGACY` in L01, the report and technical documentation describe it as implemented, and the code never had it. That's a clean, verifiable example for your AI-assisted development point: a recommendation got carried into the documentation as if it had been done.

## Answer to prompt 2 ("Find some more discrepencies like this")

I found **16 more discrepancies**, all checked against the code, the full git history, and the public GitHub Actions run list. They fall into four patterns.

**If this text is going into your Part 3 individual reflection,** the course forbids AI for that part. Use the findings below as evidence, but write the wording yourself. (The list below is evidence, not prose to paste in.)

### A. AI recommended it, the documents describe it as done, the code never had it (same pattern as `ALLOW_LEGACY`)

| # | Item | AI recommended it | Documents claim it | Code reality |
|---|---|---|---|---|
| 1 | **`protocol_version` field** | L01 `output-raw.md` ("with a protocol version field") and `output3-raw.md` ("add a protocol_version field") | Tech doc §3: "Legacy devices keep working through a protocol_version field". Report §3.5 and §5: "binds the protocol version … to the KDF" | Not in any code. [common/kex_mlkem.py](../SDMOproject/common/kex_mlkem.py) `_derive()` binds only `suite\|device_id` |
| 2 | **Migration metrics** | L01 `output-raw.md`: "Prometheus metrics, including handshake counts per suite", and the legacy-to-PQ ratio as the migration metric | Tech doc §6 lists 4 metrics (`handshakes_total{suite}`, `handshake_failures_total`, `handshake_duration_seconds`, `legacy_clients_active`). Report §2: "Metrics and logs show hybrid and legacy handshakes and failures" | No `/metrics`, no counters, no logging module anywhere. L05 is an empty template. Tech doc §1's "[share of PQ clients]" can't be filled in |
| 3 | **Device falls back from v2 to v1** | L01 `output3-raw.md`: "device.handshake(): do the v2 flow, with fallback to v1" | Report §5: "supports a controlled legacy fallback" | [device/device.py](../SDMOproject/device/device.py) imports only `kex_mlkem`, so there's no fallback. The gateway accepts legacy handshakes with no control |
| 4 | **Downgrade protection tested** | Follows from the L01 version/fallback design | Report §3.5: "Our testing makes sure that a hybrid client can not be silently downgraded" | No downgrade test exists. Tech doc §7 itself says "Not yet" |
| 5 | **Transcript in the KDF** | Risk register R11 (planned with the AI): "Include version/suite in HKDF context + transcript" | Report §3.5 / §5 imply it's done | Only the suite is bound. Public keys and ciphertexts aren't in the KDF |

### B. The AI said it had done something it hadn't

| # | AI claimed | Reality |
|---|---|---|
| 6 | L04 output: "Added a report-ready test-results table to `docs/project-report.md`" | That file has **never existed** in any commit |
| 7 | L03 `output2-raw.md`: "Pinned dependencies: exact versions in every requirements.txt" | `bench/requirements.txt` (which existed since 8 Oct, before L03) still has `requests>=2.31` and `cryptography>=42`. CI's pip-audit step doesn't scan that file |

### C. The AI flagged it as to-do; it was neither done nor recorded as a remaining risk

| # | AI recommendation (source) | Status |
|---|---|---|
| 8 | Pin the base image by digest (L03 output2) | All 3 Dockerfiles still use `FROM python:3.12-slim` |
| 9 | Pin GitHub Actions to commit SHAs; "mention this as remaining hardening" (L03 output2) | Still `@v4`/`@v5`, and not in the risk register |
| 10 | "Run the deploy job only on main" (L03 output) | `build-and-smoke-test` has no branch condition, so it runs on pull requests too |
| 11 | Upload smoke-test logs as artifacts (L03 output) | Only `coverage.xml` is uploaded |
| 12 | Add your own defects to `mutation_check.py` (L02) | 16 mutations, **0 of them on `kex_mlkem.py`**. The ML-KEM code, the main deliverable, isn't mutation-tested, yet R6 says tests are "mutation-checked (MITIGATED)" |
| 13 | Use `liboqs` (L01, L03) | The code uses `pqcrypto==0.3.4`, but tech doc §3 still says "[liboqs-python / other]" |

### D. The reverse: the AI implemented it, but the documents still say it's missing

| # | Document says | Reality |
|---|---|---|
| 14 | README "Known gaps": no tests, no CI/CD, containers run as root, unpinned dependencies. Risk register R7 ("No CI/CD") and R9 ("run as root") are not marked mitigated | Tests, CI, a non-root `app` user (uid 10001) and pinned dependencies all exist |
| 15 | Tech doc §2: SQLite "on a Docker volume (`./data`)" | The L03 LLM changed it to a named volume `cloud-data` and told the group so |
| 16 | Tech doc §7: "We don't have the ML-KEM yet", "No v2 yet" | ML-KEM was merged on 11 Oct |

### Unused evidence

In L03 the LLM told the group to *"push one commit that breaks a test … save the failing runs as evidence"*. That evidence already exists:
- 2 runs failed on 10 Oct (`bc7600c`, `b4735ef`).
- `a7e42a7` "ruff should pass" then turned CI green.
- All runs since then pass.

Tech doc §5 doesn't link these runs, though they show the pipeline blocking bad code.

The strongest examples for your point are **1–3 and 6**. They follow exactly the `ALLOW_LEGACY` pattern, and each can be checked with one `grep` or one `git log`.

## Output for prompt 3

Created on branch `ai-drift-audit` (not raw chat text, so listed here instead of pasted):

- `.claude/skills/ai-drift-audit/SKILL.md` — skill instructions (categories A–D, workflow, evidence standard, report template)
- `.claude/skills/ai-drift-audit/scripts/locate.py` — helper: where a term appears now (code / tests / docs / llm-log / external PDFs) and whether it was ever in code in any commit
- `audits/ai-drift/README.md` — where audit runs and reports are stored, with an index
- `audits/ai-drift/<date>-<commit>/` — the first audit, produced by running the skill on this repo
- this log entry
