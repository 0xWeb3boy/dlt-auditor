# Validation Card

## Metadata

- ID: `solana-2020-10-02-solana-storage-29af9d1a36`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `integer-overflow-accounting`

## What Confirmed The Issue

- Rent distribution used staked * rent_to_be_distributed with u64 operands before widening/division.
- The fixed path casts operands to u128 before multiplication and division.

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
