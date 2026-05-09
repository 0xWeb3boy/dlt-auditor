# Validation Card

## Metadata

- ID: `solana-2022-01-28-solana-validator-ops-a71f05f86c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `cpi-duplicate-account-privilege-escalation`

## What Confirmed The Issue

- Commit subject explicitly states "Fix CPI duplicate account privilege escalation".
- Patch shows duplicate account metas are normalized by OR-ing privilege bits into deduplicated instruction accounts.

## What Could Have Invalidated It

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.

## Severity Guidance

- Expected impact band: integrity_or_funds
- Expected severity band: High
- Rationale: The impact can affect funds, consensus safety, authorization boundaries, or runtime integrity when reachable.

## False-Positive Cautions

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The account or authority is derived from trusted state and cannot be chosen by the caller.
