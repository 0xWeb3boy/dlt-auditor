# Root-Cause Card

## Metadata

- ID: `solana-2019-08-21-solana-storage-e2d6f01ad3`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-genesis-blockhash-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `freshness-and-origin-validation`

## Violated Invariant

- Protocol input must satisfy freshness and origin validation before it can reach RPC method execution, account scan, or transaction forwarding.

## Trust Boundary

- Boundary: untrusted RPC caller to node query/transaction service

## Attack Surface

- Entrypoint type: JSON-RPC request or RPC transaction submission
- Sensitive sink: RPC method execution, account scan, or transaction forwarding

## Root Cause

The startup path lacked an explicit consistency check between an entrypoint-derived expected genesis blockhash and the local ledger's genesis blockhash before bank construction. The evidence supports a missing bootstrap validation guard, not a transaction parsing, storage, cryptographic forgery, or remote denial-of-service flaw.

## Impact Pattern

- Primary impact: cluster-identity-mismatch, validator-misconfiguration-prevention
- Expected band: defense_in_depth_or_input_hardening
- Severity guide: Low/Medium

## Short Reusable Lesson

The patch adds a validator startup check that compares the local ledger's genesis blockhash with an expected genesis blockhash obtained through the cluster entrypoint path. This is plausibly security-relevant cluster identity hardening, but the supplied evidence does not establish an exploitable vulnerability, attacker control, or concrete protocol impact, so it should not be treated as a confirmed security fix.
