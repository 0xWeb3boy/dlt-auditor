# Validation Card

## Metadata

- ID: `solana-2018-04-05-solana-transaction-processing-c960e8d351`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `freshness-anchor-validation`

## What Confirmed The Issue

- reserve_signature_with_last_id now returns false when last_id is not found in registered ledger IDs.
- Before the patch, an unknown last_id caused creation of a new signature set, insertion into self.last_ids, and acceptance.

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
- The signature library or sanitized message type already commits the disputed field unconditionally.
