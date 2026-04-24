# Validation Card

## Metadata

- ID: `bor-2026-04-13-bor-transaction-processing-bc8857fc8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-validation`

## What Confirmed The Issue

- Bor.Finalize changes from returning only receipts to returning ([]*types.Receipt, error), creating an authoritative rejection path in consensus finalization.
- Unexpected withdrawals and requests now return named consensus errors instead of a bare nil receipt result.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: integrity
- Expected severity band: medium

## False-Positive Cautions

- No evidence shows malformed blocks were previously accepted into canonical state.
- No exploit scenario, attacker-controlled input path, or chain split is demonstrated in the supplied patch excerpts.
