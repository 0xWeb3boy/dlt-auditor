# Validation Card

## Metadata

- ID: `solana-2021-07-01-solana-cryptography-03d213d764`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `transaction-signature-length-validation`

## What Confirmed The Issue

- RPC transaction verification now rejects transactions when `!transaction.verify_signatures_len()` before returning success.
- Ledger entry verification now conditionally rejects transactions when `verify_tx_signatures_len && !tx.verify_signatures_len()` before `verify_and_hash_message()`.

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
