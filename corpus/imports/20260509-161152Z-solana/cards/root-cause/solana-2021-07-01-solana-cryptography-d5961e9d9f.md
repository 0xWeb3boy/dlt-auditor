# Root-Cause Card

## Metadata

- ID: `solana-2021-07-01-solana-cryptography-d5961e9d9f`
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

The patch indicates incomplete explicit enforcement of the transaction signature-vector length invariant in some verification paths. The supplied evidence does not show why the existing `transaction.verify()` path was insufficient or what security consequence resulted from accepting extra signatures.

## Impact Pattern

- Primary impact: malformed-transaction-acceptance
- Expected band: defense_in_depth_or_input_hardening
- Severity guide: Low/Medium

## Short Reusable Lesson

The patch adds explicit `verify_signatures_len()` checks in RPC transaction verification and ledger entry transaction verification, and adds RPC error plumbing for signature length mismatch. The evidence supports a transaction validation/canonicality tightening for extra or mismatched signatures, but does not prove forgery, replay, double-spend, consensus divergence, or state corruption.
