# Validation Card

## Metadata

- ID: `nitro-2023-05-02-nitro-validator-ops-ccfa06f67`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unsafe-validator-configuration`

## What Confirmed The Issue

- Evidence 1: The strongest supported change is a validator/staker startup hardening in `cmd/nitro/nitro.go`: active staker strategies now auto-enable `BlockValidator` unless the dangerous override is set.
- Evidence 2: Convert a safer validator setting from manual configuration into a defaulted startup rule, while preserving an explicitly named dangerous override for opting out.

## What Could Have Invalidated It

- Compensating control 1: If the destination or mode is deterministically overwritten later, similar parameter flow may be harmless.
- Compensating control 2: If only trusted operators can invoke the path and the policy is documented, the issue may be operational hardening rather than a security bug.

## Severity Guidance

- Expected impact band: `trust_or_policy_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: If the destination or mode is deterministically overwritten later, similar parameter flow may be harmless.
- Caution 2: Do not claim theft or validator compromise without evidence that the unsafe choice reaches the final sink.
