# Validation Card

## Metadata

- ID: `bor-2026-03-18-bor-transaction-processing-70f86c4d2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-rpc-range-limit-enforcement`

## What Confirmed The Issue

- checkBlockRangeLimit(begin, end, head, api.sys.cfg.RangeLimit) was added before range-filter construction in GetLogs, GetFilterLogs, and GetBorBlockLogs.
- A new resolveBlockNumForRangeCheck helper maps symbolic negative block selectors to concrete heights specifically for range-limit enforcement.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: availability
- Expected severity band: medium

## False-Positive Cautions

- No proof that the old behavior was remotely exploitable in default or common deployments.
- No advisory, test, or commit text showing an actual denial-of-service incident or demonstrated attack.
