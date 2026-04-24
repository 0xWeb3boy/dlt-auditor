# Validation Card

## Metadata

- ID: `bor-2026-03-19-bor-transaction-processing-7d6a68d8b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion`

## What Confirmed The Issue

- GetLogs, GetFilterLogs, and GetBorBlockLogs now call checkBlockRangeLimit(...) before constructing range filters.
- The new helper resolveBlockNumForRangeCheck exists specifically to make range-limit arithmetic work for symbolic RPC block numbers.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: availability
- Expected severity band: medium

## False-Positive Cautions

- No provided hunk shows the implementation or prior absence of checkBlockRangeLimit deeper in the stack.
- No exploit, benchmark, incident, or severity evidence shows that prior behavior caused a real remotely triggerable DoS.
