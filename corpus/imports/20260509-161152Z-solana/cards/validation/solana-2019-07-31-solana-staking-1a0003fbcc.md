# Validation Card

## Metadata

- ID: `solana-2019-07-31-solana-staking-1a0003fbcc`
- Bug family: `staking_registry_and_accountability`
- Bug class: `stake-withdrawal-epoch-accounting-hardening`

## What Confirmed The Issue

- Stake withdrawal now explicitly rejects StakeState::Stake when stake.deactivated == std::u64::MAX.
- The rejected condition is labeled in-code as still activated, no can do, indicating a withdrawal eligibility guard.

## What Could Have Invalidated It

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.

## Severity Guidance

- Expected impact band: state_integrity_or_policy_bypass
- Expected severity band: Low/Medium
- Rationale: The finding is useful security-hardening evidence; severity depends on reachability and missing compensating controls.

## False-Positive Cautions

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
