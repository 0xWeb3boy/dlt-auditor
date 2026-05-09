# Validation Card

## Metadata

- ID: `solana-2020-05-08-solana-cryptography-f98bfda6f9`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `disabled-signature-verification-path`

## What Confirmed The Issue

- Vote verification previously accepted a sigverify_disabled parameter and could call ed25519_verify_disabled.
- After the patch, vote verification always calls sigverify::ed25519_verify_cpu.

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
