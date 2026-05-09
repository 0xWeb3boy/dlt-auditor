# Root-Cause Card

## Metadata

- ID: `solana-2019-05-20-solana-transaction-processing-ead15d294e`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `panic-prone-input-parsing`
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

The supported root cause is panic-prone parsing of untrusted RPC/pubsub parameters via unwrap() before normal InvalidParams-style handling. Security impact beyond that panic-prone path is not established.

## Impact Pattern

- Primary impact: denial-of-service
- Expected band: availability_or_resource_exhaustion
- Severity guide: Medium

## Short Reusable Lesson

The grounded change is in core/src/rpc_pubsub.rs: account_subscribe, program_subscribe, and signature_subscribe replace direct bs58 decoding with unwrap() by fallible typed parameter parsing. This is plausibly defensive input handling, but the evidence does not prove a security vulnerability, whole-node crash, consensus impact, signature bypass, replay issue, or state corruption. The added get_epoch_vote_accounts RPC appears to be the main feature chang...
