# Validation Card

## Metadata

- ID: `solana-2020-08-17-solana-staking-d9ae092637`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `rent-exemption-recheck-bypass`

## What Confirmed The Issue

- Runtime rent collection changed from unconditional rent_epoch advancement to conditional advancement for exempt accounts.
- Inline comment states exempt status must be checked again later in the current epoch.

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
