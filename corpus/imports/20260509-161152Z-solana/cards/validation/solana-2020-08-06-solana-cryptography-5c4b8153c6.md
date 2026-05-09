# Validation Card

## Metadata

- ID: `solana-2020-08-06-solana-cryptography-5c4b8153c6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-off-curve-address-validation`

## What Confirmed The Issue

- Adds `tweetnacl` low-level access for curve membership checking.
- Changes program address derivation to compute `publicKeyBytes` and call `is_on_curve(publicKeyBytes)`.

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
