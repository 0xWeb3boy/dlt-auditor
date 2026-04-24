# Validation Card

## Metadata

- ID: `bor-2026-04-16-bor-transaction-processing-11ecb6aa7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-validation`

## What Confirmed The Issue

- Bor.Finalize now returns ([]*types.Receipt, error) instead of only receipts, creating an explicit failure channel in consensus finalization.
- Unexpected withdrawals and requests are now rejected with typed consensus errors instead of returning nil receipts silently.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: integrity
- Expected severity band: medium

## False-Positive Cautions

- No evidence shows a concrete pre-patch exploit, consensus split, or attacker-triggerable acceptance of invalid blocks.
- The cited commit message mentions a state-sync type check, but the actual type-validation hunk is not included here.
