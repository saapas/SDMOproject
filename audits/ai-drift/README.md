# AI drift audits

Reports from the [`ai-drift-audit`](../../.claude/skills/ai-drift-audit/SKILL.md) skill.

**What it checks:** places where an LLM recommended or claimed something, it was carried into the
documentation or report as if it existed, but it was never implemented in code — and the reverse
(implemented, but the docs still say it is missing).

Example that started this: the LLM recommended an `ALLOW_LEGACY` flag
(`llm-log/L01-legacy-system/output3-raw.md`), the report and technical documentation describe it as
the migration control, and it is not in any code file in any commit.

## Running an audit

In Claude Code, from the repository root, ask for example:

> Run an AI drift audit on this repo. The report and technical documentation are in
> ~/Downloads/Project Report Group 19.pdf and ~/Downloads/Technical Documentation.pdf.

Without Claude Code, follow the workflow in the skill's `SKILL.md` by hand. The helper script
works on its own:

```bash
python .claude/skills/ai-drift-audit/scripts/locate.py ALLOW_LEGACY protocol_version \
    --external "path/to/report.pdf"      # pypdf needed only for PDFs
```

Each run goes in its own folder, `<YYYY-MM-DD>-<commit>/`, containing `report.md` (findings) and
`evidence.md` (commands and raw output, so every finding can be re-checked).

## Index

| Date | Commit | Report | A | B | C | D |
|---|---|---|---|---|---|---|
| 2026-10-11 | 1c80362 | [report](2026-10-11-1c80362/report.md) · [evidence](2026-10-11-1c80362/evidence.md) | 5 | 2 | 5 | 5 |
