# Validation Card

## Metadata

- ID: `solana-2021-03-11-solana-core-logic-cc38ae72e7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `writable-account-boundary-hardening`

## What Confirmed The Issue

- Deserializer now receives a skip_ro_deserialization policy flag.
- Unaligned deserialization now gates account-state copy-back on keyed_account.is_writable() or disabled readonly skipping.

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
- The account or authority is derived from trusted state and cannot be chosen by the caller.
