# Validation Card

## Metadata

- ID: `solana-2018-12-01-solana-cryptography-34c3a0cc1f`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `gossip-signature-verification-hardening`

## What Confirmed The Issue

- Commit subject states: Add signature verification to gossip.
- CRDS value variants gain signature-bearing data, including Vote.signature and LeaderId Signable behavior.

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
