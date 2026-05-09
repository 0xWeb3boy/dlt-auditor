# Validation Card

## Metadata

- ID: `solana-2021-09-02-solana-validator-ops-afb87a386a`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unsafe-key-reuse`

## What Confirmed The Issue

- Commit body says the authorized withdrawer should not be the vote account keypair or validator identity keypair for security reasons.
- The CLI now requires an explicit authorized_withdrawer instead of allowing omission and defaulting to identity_pubkey.

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
