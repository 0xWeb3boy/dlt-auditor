# Validation Card

## Metadata

- ID: `solana-2019-03-01-solana-staking-db825b6e26`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `missing-signature-check`

## What Confirmed The Issue

- process_vote now rejects keyed_accounts[0] when signer_key() is none before deserializing and mutating VoteState.
- The removed entrypoint-level blanket signer check is replaced with instruction-specific signer enforcement for Vote processing.

## What Could Have Invalidated It

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.

## Severity Guidance

- Expected impact band: state_integrity_or_policy_bypass
- Expected severity band: High
- Rationale: The impact can affect funds, consensus safety, authorization boundaries, or runtime integrity when reachable.

## False-Positive Cautions

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The signature library or sanitized message type already commits the disputed field unconditionally.
