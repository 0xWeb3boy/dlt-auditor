# Validation Card

## Metadata

- ID: `optimism-2025-10-23-optimism-transaction-processing-5f5e50fa73`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `fork-activation-validation-gap`

## What Confirmed The Issue

- batches.go expands the rejection rule to drop non-empty batches on Jovian activation blocks, not just Interop.
- types.go adds Jovian recognition to activation-block detection, which is directly used by validation logic.
- Tests assert that upgrade blocks from Jovian onward must not contain user transactions unless explicitly exempted.
- The changed logic sits in rollup batch-validation and fork-activation handling, which are consensus-sensitive code paths.

## What Could Have Invalidated It

- No proof that this omission was exploitable by an untrusted party in production.
- No demonstrated chain split, fund-loss, or concrete safety/liveness incident tied to the bug.
- No evidence showing which actor could inject the invalid batch under real deployment conditions.
- an earlier boundary already rejects the same malformed field under all reachable modes

## Severity Guidance

- Expected impact band: consensus-or-state-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No proof that this omission was exploitable by an untrusted party in production.
- No demonstrated chain split, fund-loss, or concrete safety/liveness incident tied to the bug.
- No evidence showing which actor could inject the invalid batch under real deployment conditions.
