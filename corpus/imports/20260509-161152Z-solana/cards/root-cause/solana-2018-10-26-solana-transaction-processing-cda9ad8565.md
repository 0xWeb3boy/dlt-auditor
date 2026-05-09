# Root-Cause Card

## Metadata

- ID: `solana-2018-10-26-solana-transaction-processing-cda9ad8565`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `incomplete-signature-verification`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `signature-and-signer-binding`

## Violated Invariant

- Protocol input must satisfy signature and signer binding before it can reach account balance/state mutation, fee/rent accounting, nonce state, or transaction commitment.

## Trust Boundary

- Boundary: signed client transaction to bank accounting and execution state

## Attack Surface

- Entrypoint type: transaction admission, sanitization, or execution path
- Sensitive sink: account balance/state mutation, fee/rent accounting, nonce state, or transaction commitment

## Root Cause

The packet verification logic handled signature verification as a single-signature check even though the transaction layout could declare multiple signatures. The missing check was iteration over the declared signature count during packet-level verification.

## Impact Pattern

- Primary impact: authorization-integrity
- Expected band: defense_in_depth_or_input_hardening
- Severity guide: Low/Medium

## Short Reusable Lesson

The patch likely fixes incomplete packet-level signature verification for transactions with multiple signatures. In src/sigverify.rs::verify_packet, the old code performed one Ed25519 signature::verify call, while the patched code loops over sig_len, checks each signature/public-key range against packet.meta.size, and verifies each pair over the message. The evidence supports a cryptographic authorization bug at the packet verifier level, but does not e...
