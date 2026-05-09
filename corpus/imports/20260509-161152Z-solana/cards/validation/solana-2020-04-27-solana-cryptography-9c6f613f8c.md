# Validation Card

## Metadata

- ID: `solana-2020-04-27-solana-cryptography-9c6f613f8c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `protocol-input-validation`

## What Confirmed The Issue

- Commit subject states deserialized input values were not sanitized and claims financial impact.
- CRDS data now dispatches through Sanitize and rejects vote indices greater than or equal to MAX_VOTES.

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
