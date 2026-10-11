---
name: ai-drift-audit
description: Audit a repository for "AI drift" — places where an LLM recommended or claimed something (in LLM/prompt logs), it was carried into documentation or the report as if it existed, but it was never implemented in code; plus the reverse (implemented, but docs still say missing). Produces an evidence-backed, dated report under audits/ai-drift/. Use this whenever someone wants to check that documentation, a report or a submission matches the code, asks "did we actually implement X?", wants to verify what an AI said it did, reviews an LLM log, prepares a project submission or peer review, or suspects that docs overstate the code — even if they don't say "drift".
---

# AI drift audit

## Why this exists

When an LLM helps build a project, its recommendations end up in three places: the LLM log
(what it suggested), the documentation and report (what the team says the system does), and the
code (what the system actually does). These drift apart quietly. The LLM proposes a feature, the
feature is written into the plan, the plan text is reused in the report, and nobody notices that
the feature was never built.

Real example from this repository: in `llm-log/L01-legacy-system/output3-raw.md` the LLM
recommended *"keep the v1 path behind an ALLOW_LEGACY flag"*. The project report and the technical
documentation both describe `ALLOW_LEGACY` as the migration control. It is not in any code file in
any commit. A reader trusting the report would believe legacy clients can be switched off; in
reality the gateway accepts them unconditionally.

The audit's job is to find these gaps with evidence a human can re-check in one command, so the
team can either implement the feature or correct the documentation before someone else finds it.

## What counts as a finding

| Category | Pattern | Example |
|---|---|---|
| **A. Recommended → documented → not implemented** | The LLM suggested it, the docs/report present it as existing, code never had it | `ALLOW_LEGACY`, `protocol_version` |
| **B. Claimed done → does not exist** | The LLM said "I added / created / pinned X", but X is absent | "Added a table to docs/project-report.md" — file never existed |
| **C. To-do → neither done nor recorded** | The LLM said "you should / remaining hardening: X"; not implemented and not in the risk register or docs as open work | Pin base image by digest |
| **D. Reverse drift** | Implemented (often by the LLM itself), but docs still say it is missing or describe an older design | README says "no CI" while CI exists |

Something that is recommended, not implemented, and honestly listed as open work is **not** a
finding — that is the system working as intended. Mention it under "checked and consistent".

Boundary rules, because documents often disagree with each other:

- **The documents that get read decide.** If an item is honestly listed as open in the repo (say,
  the risk register) but a report, submission or README presents it as done, it is an A finding.
  Note the internal inconsistency in the finding.
- **Split partial truths.** "Binds the version and suite into the KDF" when only the suite is bound:
  list the true part under "checked and consistent" and report only the false part.
- **Verification claims count too.** Statements like "mutation-checked", "covered by tests" or
  "scanned by pip-audit" drift silently when new code is added later. Check that they still cover
  the *newest* code (e.g. do any mutations target the module added last?).
- **Doc-vs-code gaps with no LLM origin**, or that fit no category, go under "Other observations".

## Inputs to gather first

1. **Repository root** and current commit (`git rev-parse --short HEAD`, branch). All evidence is
   relative to this commit; write it in the report. If `git status` shows uncommitted changes, say so
   in the report — the helper searches the committed HEAD, not the working tree.
2. **LLM logs**: folders like `llm-log/`, `ai-log/`, `prompts/`. Read the *raw outputs*, not only the
   team's summaries — recommendations and claims live in the raw text. Also read their **history**
   (`git log -p -- llm-log/`): raw outputs get replaced, and the version that shaped the documents may
   only exist in an old commit. The helper prints the oldest matching version when a term is gone
   from HEAD.
3. **Documentation in the repo**: README, `docs/`, risk register, architecture notes.
4. **Documents outside the repo**: the report, technical documentation, slides (often PDFs the user
   attaches or keeps in Downloads). Ask for their paths if not given; they are where drift matters
   most, because they are what gets graded or shipped.
5. **Code**: everything else that executes — source, tests, CI workflows, Dockerfiles, compose files,
   dependency files.

## Workflow

### 1. Extract candidate items

Read the LLM raw outputs and the documents, and list every *checkable* statement:

- identifiers, flags, environment variables, config keys (`ALLOW_LEGACY`)
- fields, endpoints, metric names (`protocol_version`, `/metrics`, `handshakes_total`)
- file paths the LLM said it created or changed
- dependencies and versions ("exact versions in every requirements.txt")
- behaviours ("the device falls back to v1", "binds the version into the KDF", "tests prevent downgrade")
- to-dos the LLM handed back ("pin the base image by digest", "run deploy only on main")

Behaviour claims have no single token to grep for; note which function or file would have to
implement them so you can read it in step 2.

### 2. Verify each item against the code

Run the bundled helper for token-like items. It reports matches at HEAD by category
(code / tests / docs / llm-log) and walks every commit on every branch, so you can tell
"never implemented" apart from "implemented and later removed":

```bash
python .claude/skills/ai-drift-audit/scripts/locate.py ALLOW_LEGACY protocol_version \
    --external ~/Downloads/report.pdf ~/Downloads/technical-doc.pdf
```

(`pypdf` is needed only for `--external` PDFs; without it, read the PDFs yourself. Diagrams and
other images in PDFs are not searched — say so under "Limits".)

The helper's output is mechanical. Its "described but never in code" hint fires for any term,
including ones that aren't features (a model name, a word like "approved"), and matches marked
"(loose match)" only matched because `_`, `-` and spaces were treated as equal — check those before
quoting them.

Then **read the code** that would implement the item. A grep result is a lead, not proof:

- A match can be a false positive (`Counter(` matches `time.perf_counter()`; a name in a comment
  or string is not an implementation).
- A missing match can be a false negative (the feature exists under another name). Search for
  synonyms and read the function that would own the behaviour.
- For behaviour claims, open the function and check what it actually does (e.g. what goes into
  the KDF `info`, whether the device ever calls the legacy handshake).

Re-check any doc claim about tests by finding the test: is it there, is it marked `xfail`/skipped?

### 3. Classify and rate confidence

Put each item into A–D or "checked and consistent". Rate each finding:

- **Confirmed** — the code was read and the evidence is unambiguous.
- **Likely** — strong evidence, but a synonym or indirect implementation can't be fully ruled out.
- **Needs human check** — depends on runtime behaviour or intent you can't verify by reading.

Do not run the project's code to "prove" something; reading code and git history is enough and
avoids side effects. If a claim can only be settled by running tests, say so and leave it to a human.

### 4. Write the report

Create `audits/ai-drift/<YYYY-MM-DD>-<shortsha>/` (local date) and write:

- `report.md` — using the template below
- `evidence.md` — the raw helper output and every other command you ran with its output, so each
  finding can be re-checked. Use this shape per entry:

  ````markdown
  ### A1 ALLOW_LEGACY
  ```text
  $ git grep -n -i -E "allow[_ -]?legacy" HEAD -- gateway device common
  (no output)
  ```
  ````

Then add one row to the index table in `audits/ai-drift/README.md`.

If you cannot write files (for example when running as a sub-agent whose harness only allows
returning text), return the full `report.md` and `evidence.md` contents and the index row in your
reply, so the caller can save them unchanged.

Keep the tone factual. The point is to help the team fix things, not to assign blame; refer to
"the LLM", "the report", "the code", not to people.

## Report template

```markdown
# AI drift audit — <repo> @ <shortsha> (<YYYY-MM-DD>)

**Scope:** <logs, docs and external documents read; code paths checked>
**Method:** ai-drift-audit skill; helper `locate.py`; code read for every finding.

## Summary
| Category | Findings |
|---|---|
| A. Recommended → documented → not implemented | n |
| B. Claimed done → does not exist | n |
| C. To-do → neither done nor recorded | n |
| D. Reverse drift (implemented, docs outdated) | n |

<2–3 sentences: the most important gaps and what a reader of the report would wrongly believe.>

## Findings

### A1. <short title>  — Confirmed
- **LLM said:** "<quote>" — `<file>:<line>`
- **Documented as:** "<quote>" — `<doc>` <section/page>
- **Code:** <what exists instead, with file:line> — evidence: `<command>` → <result>
- **History:** <never in code in N commits / removed in <sha>; quote old sources as `git show <sha>:<path>`>
- **Suggested action:** implement <x> | or change <doc section> to describe it as open work

(repeat per finding; group by category)

## Checked and consistent
<bullets: items verified as implemented, or honestly documented as open — shows coverage>

## Other observations (outside A–D)
<doc-vs-code mismatches with no LLM origin, overwritten results, wording problems>

## Limits of this audit
<what was not checked, documents or images not readable, uncommitted changes, claims that need running tests>
```

## After the audit

Running this skill is itself AI-assisted work. If the repository keeps an LLM log, suggest adding
an entry (prompt, the report as output, what the team accepted or rejected from it).
