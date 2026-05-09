# Validation Card

## Metadata

- ID: `solana-2020-11-13-solana-transaction-processing-f6b65b033e`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `arithmetic-overflow-in-validation-counter`

## What Confirmed The Issue

- Commit message explicitly says it fixes overflow in entry tick/hash count verification.
- Runtime validation code changes `*tick_hash_count += entry.num_hashes` to `saturating_add`.

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
