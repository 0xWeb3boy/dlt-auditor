# Validation Card

## Metadata

- ID: `solana-2019-07-31-solana-staking-9278201198`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-withdrawal-state-guard`

## What Confirmed The Issue

- Production withdrawal path adds an explicit guard for stake.deactivated == std::u64::MAX with the comment 'still activated, no can do'.
- Withdrawal accounting changes from clock.epoch to clock.stakers_epoch, matching the staker epoch basis used elsewhere.

## What Could Have Invalidated It

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.

## Severity Guidance

- Expected impact band: defense_in_depth_or_input_hardening
- Expected severity band: Low/Medium
- Rationale: The finding is useful security-hardening evidence; severity depends on reachability and missing compensating controls.

## False-Positive Cautions

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
