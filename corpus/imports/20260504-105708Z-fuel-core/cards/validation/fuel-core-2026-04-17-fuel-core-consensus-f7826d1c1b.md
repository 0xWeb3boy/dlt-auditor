# Validation Card

## Metadata

- ID: `fuel-core-2026-04-17-fuel-core-consensus-f7826d1c1b`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `consensus-liveness`
- Security verdict: `likely`
- Validated as: `security-hardening`

## What Confirmed The Issue

- Patch changes HashMap key from (u64, BlockId) to BlockId with max_epoch metadata.
- Regression test reproduces the April 17 devnet deadlock.

## What Could Have Invalidated It

- Block id does not uniquely identify the committed object in this protocol.
- A separate quorum layer normalizes epoch before this grouping.

## Severity Guidance

- Expected impact band: `medium`
- Expected severity band: `medium`
- Rationale: Misgrouping identical blocks can deadlock leader reconciliation and halt progress. The case is likely hardening because attacker triggerability is not established.

## False-Positive Cautions

- No issue if epoch is part of canonical block identity.
- No issue if mismatched epochs indicate genuinely different consensus objects that must not be grouped.
