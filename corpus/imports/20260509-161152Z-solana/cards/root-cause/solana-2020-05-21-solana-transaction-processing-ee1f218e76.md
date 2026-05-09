# Root-Cause Card

## Metadata

- ID: `solana-2020-05-21-solana-transaction-processing-ee1f218e76`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `rpc-input-validation-panic-hardening`
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

RPC parameter validation used an unchecked unwrap for base58 transaction decoding and mapped several malformed client-parameter cases to generic request errors. The provided evidence does not prove state corruption, consensus impact, authentication bypass, ledger mutation, validator shutdown, or a confirmed remote denial of service.

## Impact Pattern

- Primary impact: availability-hardening
- Expected band: availability_or_resource_exhaustion
- Severity guide: Medium

## Short Reusable Lesson

The patch changes RPC parameter error handling in `core/src/rpc.rs`. The strongest grounded change is replacing an unchecked `bs58::decode(...).into_vec().unwrap()` in `deserialize_bs58_transaction` with fallible error propagation returning `InvalidParams`. Other changes reclassify oversized transactions, transaction deserialization failures, pubkey parse failures, and signature parse failures from `InvalidRequest` to `InvalidParams`. The evidence suppo...
