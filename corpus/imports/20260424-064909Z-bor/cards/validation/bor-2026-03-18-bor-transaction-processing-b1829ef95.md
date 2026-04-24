# Validation Card

## Metadata

- ID: `bor-2026-03-18-bor-transaction-processing-b1829ef95`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion-hardening`

## What Confirmed The Issue

- Adds checkBlockRangeLimit(...) before constructing range filters in GetLogs.
- Adds the same range-limit guard in GetFilterLogs, closing an alternate query path.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: availability
- Expected severity band: medium

## False-Positive Cautions

- No proof that the affected RPC methods were exposed to untrusted callers in typical deployments.
- No demonstrated CPU, memory, disk, or latency exhaustion from the pre-patch behavior.
