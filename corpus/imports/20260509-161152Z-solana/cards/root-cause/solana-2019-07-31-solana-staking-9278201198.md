# Root-Cause Card

## Metadata

- ID: `solana-2019-07-31-solana-staking-9278201198`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-withdrawal-state-guard`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `stake-accountability-invariant`

## Violated Invariant

- Protocol input must satisfy stake accountability invariant before it can reach stake delegation, withdrawal, reward accounting, vote authority, or validator weight.

## Trust Boundary

- Boundary: signed stake/vote instruction to stake-weighted accounting state

## Attack Surface

- Entrypoint type: stake or vote program instruction
- Sensitive sink: stake delegation, withdrawal, reward accounting, vote authority, or validator weight

## Root Cause

The withdrawal path did not directly enforce the still-activated stake lock in the provided before hunk and used `clock.epoch` rather than `clock.stakers_epoch` for the staked-balance calculation. The evidence supports an epoch/accounting mismatch and missing withdrawal guard, but does not prove a concrete external exploit path.

## Impact Pattern

- Primary impact: stake-lock-integrity, premature-withdrawal-prevention
- Expected band: defense_in_depth_or_input_hardening
- Severity guide: Low/Medium

## Short Reusable Lesson

The grounded security-relevant change is in the stake withdrawal path. The patch adds an explicit rejection when `stake.deactivated == std::u64::MAX`, described in-code as still activated, and changes the withdrawal stake calculation from `clock.epoch` to `clock.stakers_epoch`. The supplied bank changes are test evidence for epoch vote-account accounting, not production runtime logic.
