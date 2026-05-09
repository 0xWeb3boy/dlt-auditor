# Root-Cause Card

## Metadata

- ID: `solana-2021-07-01-solana-cryptography-03d213d764`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `transaction-signature-length-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `signature-format-validation`

## Violated Invariant

- Protocol input must satisfy signature format validation before it can reach RPC method execution, account scan, or transaction forwarding.

## Trust Boundary

- Boundary: untrusted RPC caller to node query/transaction service

## Attack Surface

- Entrypoint type: JSON-RPC request or RPC transaction submission
- Sensitive sink: RPC method execution, account scan, or transaction forwarding

## Root Cause

The observed transaction verification paths lacked an explicit structural check for signature-vector length before accepting or hashing a transaction as verified.

## Impact Pattern

- Primary impact: invalid-transaction-admission
- Expected band: defense_in_depth_or_input_hardening
- Severity guide: Low/Medium

## Short Reusable Lesson

The patch adds explicit `verify_signatures_len()` checks in RPC transaction verification and ledger entry verification/hashing paths. The evidence supports a security-relevant transaction validation hardening for rejecting transactions with extra or otherwise invalid signature counts, but it does not establish a concrete exploit such as forgery, replay, double-spend, or consensus divergence.
