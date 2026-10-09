# L02: Dockerfiles

- **LLM and version:** Claude Sonnet 5.5
- **Goal:** To provide tests for the legacy system

## Context provided
All the previous texts

## Prompt
```text
we got this part finished and now move on to write the tests for this system. Write the tests.
```

## Output
See output-raw.md

## Review: issues found
Some tests were loose and unneccessary and we added defections. For example test_gateway_id_is_added_before_forwarding is tested already in another test.
est_garbage_input_is_exactly_401_and_never_forwarded was tightened by the request from the llm.
We added to mutuations some entries that were suggested.
Other than that the tests looked great and had great coverage.

## Decision
**Accepted / Modified / Rejected:** Modified

## Verification
Reviewed and ran the tests

## Remaining risk
Can't test for everything and we or the AI can for sure have blind spots.
