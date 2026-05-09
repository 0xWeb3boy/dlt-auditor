# Root-Cause Card

## Metadata

- ID: `solana-2020-08-05-solana-transaction-processing-7b8e5a9f47`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-transaction-sanitization`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-shape-validation`

## Violated Invariant

- Protocol input must satisfy input shape validation before it can reach RPC method execution, account scan, or transaction forwarding.

## Trust Boundary

- Boundary: untrusted RPC caller to node query/transaction service

## Attack Surface

- Entrypoint type: JSON-RPC request or RPC transaction submission
- Sensitive sink: RPC method execution, account scan, or transaction forwarding

## Root Cause

The RPC preflight simulation batch path skipped explicit structural transaction sanitization before constructing its TransactionBatch, unlike paths that already called tx.sanitize().

## Impact Pattern

- Primary impact: input-validation, defense-in-depth
- Expected band: state_integrity_or_policy_bypass
- Severity guide: Low/Medium

## Short Reusable Lesson

The patch adds transaction sanitization to Solana RPC preflight simulation batch preparation. The evidence supports a missing validation fix for malformed transaction structure, specifically an invalid program_id_index in a preflight test. It does not establish an exploitable security vulnerability or concrete impact beyond clean rejection of malformed input.
