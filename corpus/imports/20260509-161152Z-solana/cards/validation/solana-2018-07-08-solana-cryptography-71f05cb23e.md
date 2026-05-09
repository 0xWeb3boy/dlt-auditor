# Validation Card

## Metadata

- ID: `solana-2018-07-08-solana-cryptography-71f05cb23e`
- Bug family: `authz_and_role_gates`
- Bug class: `timestamp-source-authorization`

## What Confirmed The Issue

- Commit message says contracts should not trust the network for timestamps.
- Budget::apply_witness now receives a source PublicKey and passes it into condition checks.

## What Could Have Invalidated It

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.

## Severity Guidance

- Expected impact band: integrity_or_funds
- Expected severity band: Low/Medium
- Rationale: The finding is useful security-hardening evidence; severity depends on reachability and missing compensating controls.

## False-Positive Cautions

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The account or authority is derived from trusted state and cannot be chosen by the caller.
