# Validation Card

## Metadata

- ID: `solana-2021-01-09-solana-staking-4470afceaa`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `authority-model-hardening`

## What Confirmed The Issue

- Upgradeable loader SetAuthority now matches Buffer state and checks authority_address.
- Buffers with no authority are rejected as immutable via InstructionError::Immutable.

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
- The account or authority is derived from trusted state and cannot be chosen by the caller.
