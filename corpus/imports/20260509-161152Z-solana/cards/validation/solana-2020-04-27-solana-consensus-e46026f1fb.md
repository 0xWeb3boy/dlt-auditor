# Validation Card

## Metadata

- ID: `solana-2020-04-27-solana-consensus-e46026f1fb`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-deserialization-validation`

## What Confirmed The Issue

- Adds validation for deserialized protocol objects via Sanitize implementations.
- Rejects out-of-range slot and wallclock values in CRDS-related structures.

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
