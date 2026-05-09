# Validation Card

## Metadata

- ID: `solana-2019-11-03-solana-consensus-d9a9d6547f`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-identity-binding`

## What Confirmed The Issue

- Commit subject explicitly identifies incorrectly signed CrdsValues.
- Patch removes Signable implementation for CrdsValue that delegated signing and verification across variants.

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
