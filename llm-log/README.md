# LLM log

All significant LLM-assisted work is logged here. The LLM is treated as an untrusted assistant;
every artefact is reviewed, verified and then accepted, modified or rejected.

- **LLM and version:** [fill in, e.g. model name and interface]
- **Rule:** log the same day. Copy prompts verbatim. Keep raw outputs unedited. Never include secrets.
- **Structure:** one folder per artefact: `entry.md` (prompt, context, review, decision),
  `output-raw.md` (unedited LLM answer), and a link or `final.diff` for our changes.
- **Iterations:** if you re-prompt, keep each round as `prompt-2.md`, `output-raw-2.md`, and so on.

## Index (mirror this in section 8 of the technical documentation)

| ID | Artefact | Folder | Decision | Main finding | Remaining risk |
|---|---|---|---|---|---|
| L01 | Test suite | [L01-test-suite](L01-test-suite/entry.md) | [ ] | [ ] | [ ] |
| L02 | Dockerfiles | [L02-dockerfiles](L02-dockerfiles/entry.md) | [ ] | [ ] | [ ] |
| L03 | CI workflow | [L03-ci-workflow](L03-ci-workflow/entry.md) | [ ] | [ ] | [ ] |
| L04 | ML-KEM integration | [L04-mlkem-integration](L04-mlkem-integration/entry.md) | [ ] | [ ] | [ ] |
| L05 | Metrics and logging | [L05-metrics-logging](L05-metrics-logging/entry.md) | [ ] | [ ] | [ ] |

## Review checklist (use when filling in "issues found")

- Correctness: does it do what was asked? Does it run? Are API/function names real?
- Security: key derivation (no raw secrets as keys), nonce handling, error handling, secrets in logs or config, downgrade paths
- Maintainability: structure, naming, duplication, comments that match the code
- Testability: do the tests assert real behaviour? Do they fail when the code is broken (inject a defect)?
- Operations: root user, unpinned images, health checks, resource use, log content
- Performance: compare against `docs/baseline-results.md`
