# Validation Card

## Metadata

- ID: `solana-2018-10-26-solana-transaction-processing-cda9ad8565`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `incomplete-signature-verification`

## What Confirmed The Issue

- src/sigverify.rs changed verify_packet from one signature::verify call to a loop over sig_len.
- The patched code verifies each signature/public-key pair against the transaction message.

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
