# L01: Test suite

- **Date / author:** [ ]
- **LLM and version:** [ ]
- **Goal:** [one sentence]

## Context provided
[files pasted, constraints and instructions given]

## Prompt
```text
[exact prompt, verbatim]
```

## Output
See output-raw.md. Summary: [3 to 4 lines]

## Review: issues found
| # | Issue | How found | Severity |
|---|---|---|---|
| 1 | [ ] | [code review / test / static analysis / ran it] | [ ] |

*Things to look for:* tests that only check status codes; missing failure cases (tampered ciphertext, unknown session, bad key); tests that still pass after you inject a defect (skip tag check, reuse nonce)

## Decision
**Accepted / Modified / Rejected:** [what, and why]
**Our changes:** [commit link or final.diff]

## Verification
[tests added, commands run, CI link, results]

## Remaining risk
[what is still uncertain or untrusted]
