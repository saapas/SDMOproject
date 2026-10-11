# L06: AI drift audit (recommended → documented → never implemented)

- **Date / author:** 2026-10-11 / Abdullah Al Mazed
- **LLM and version:** Claude Opus 5.5 (Claude Code, VS Code extension)
- **Goal:** Check whether what the LLM recommended or claimed, and what our report and technical
  documentation say, is actually in the code — and turn that check into a reusable skill.

## Context provided
- This repository (cloned at commit `1c80362`), including all of `llm-log/`
- The group's draft `Project Report Group 19.pdf` and `Technical Documentation.pdf` (not in the repo)
- Earlier in the same session the LLM had read the LLM log and listed issues in our AI-assisted
  process (shallow verification, unverified claims, lost context when switching LLMs)

## Prompts
Prompt 1, after the LLM pointed out that `ALLOW_LEGACY` appears in the report but not in the code:
```text
reconfirm : No ALLOW_LEGACY anywhere.
```

Prompt 2:
```text
We noticed discrepancies where AI recommended something, it got carried into documentation but was never implemented.

An example: ALLOW_LEGACY was planned and documented together with AI, but turns out in the end it was never implemented. We can see llm-log/L01-legacy-system/output3-raw.md has the LLM's recommendation "keep the v1 path behind an ALLOW_LEGACY flag". But not commit has been put in the code.

Find some more discrepencies like this
```

Prompt 3:
```text
write a skill to do this analysis. We noticed discrepancies where AI recommended something, it got carried into documentation but was never implemented.

An example: ALLOW_LEGACY was planned and documented together with AI, but turns out in the end it was never implemented

Add this to prompt log, create a new directory where such runs and reports are stored. When done, review with me and creeate a pull request
```

## Output
See [output-raw.md](output-raw.md). Summary:
- Prompt 1: confirmed `ALLOW_LEGACY` is in no code file in any of the 45 commits — only in the LLM
  log (and in the two PDFs). Corrected its own earlier wording "not anywhere" to "never in code".
- Prompt 2: 16 more discrepancies in four patterns (recommended→documented→not implemented;
  claimed done but absent; to-dos neither done nor recorded; reverse drift).
- Prompt 3: the skill `.claude/skills/ai-drift-audit/` (instructions + helper script `locate.py`),
  the reports folder `audits/ai-drift/`, and a first audit report produced by running the skill.

## Review: issues found
| # | Issue | How found | Severity |
|---|---|---|---|
| 1 | LLM first said "No ALLOW_LEGACY anywhere"; it is in `llm-log/` (and the PDFs), just not in code | Asked the LLM to reconfirm; it searched all files, branches and history | Low (wording) |
| 2 | One check in the LLM's search matched `time.perf_counter()` when looking for metric `Counter(` — a false positive | LLM noticed it when reading the matches | Low |
| 3 | Manual list (prompt 2) had a false positive: it flagged the tech doc's `./data` volume, but that section describes the baseline, which really used `./data` | The skill's test run classified it as consistent; re-read the doc section | Low |
| 4 | Test run of the skill missed one real finding: mutation testing (`tests/mutation_check.py`) has 0 mutations on `kex_mlkem.py` | Compared the run's findings with the manual list | Medium |
| 5 | Test run found 6 things the manual list missed, most importantly that the L01 raw output which contains the `ALLOW_LEGACY` three-phase plan and the four metric names was overwritten in `d362548` (only visible in git history) | Read the run's report, re-checked each claim with `git show` / `grep` | — (improvement) |
| 6 | Skill/helper problems reported by the test run: helper searched the working tree instead of HEAD; PDF line breaks split identifiers; old log versions only shown as counts; sub-agents can't write report files; unclear A/C boundary and partial truths | The test run's own feedback | Medium |
| 7 | The helper's "never in code" hint fires for non-features (model names, ordinary words), and loose matching (`_`/`-`/space) gives false hits | Test run feedback | Low |

## Decision
**Accepted / Modified / Rejected:** Modified — pending group review in the pull request.
- Skill and helper: modified after the test run (fixes for issues 4, 6, 7: HEAD-only search,
  dirty-tree warning, `(loose match)` flag, PDF whitespace normalisation, quoting of overwritten log
  versions, rules for A/C boundary, partial truths and verification claims, sub-agent fallback).
- First audit report: accepted as produced, plus a "Reviewer notes" section (verification of the new
  claims and the missed finding C5).
- Manual finding about `./data` (issue 3): rejected.

## Verification
- Helper script reproduces the manual findings for `ALLOW_LEGACY`, `protocol_version`,
  `handshakes_total` (described, never in code in any commit) and `cloud-data` (in code)
- `ruff check .` (our CI config) passes; `bandit -ll` reports no medium/high issues on the script
- Test run of the skill on this repo by a fresh sub-agent with no access to the manual findings:
  16 findings; 14 of the 16 manual findings reproduced, 1 missed (C5, added in review), 1 manual
  finding shown to be a false positive, 6 new findings
- Every new claim in the run's report re-checked by hand (commands in
  `audits/ai-drift/2026-10-11-1c80362/evidence.md`, section 4)
- Improved helper re-run: finds `handshake_failures_total` in the PDF despite a line break, quotes
  the overwritten L01 source with `git show`, warns about uncommitted changes

## Remaining risk
- The audit reads code and history; it does not run the system, so behaviour that only shows at
  runtime is out of scope.
- The skill's findings are LLM output too and need the same review as any other artefact.
- Only one test run; the improved skill has not been re-run end to end.
- The audit report names gaps in our own report and technical documentation; the group decides
  whether to implement the features or correct the documents.
