# Code-Shape Card

## Metadata

- ID: `solana-2020-05-21-solana-transaction-processing-ee1f218e76`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `rpc-input-validation-panic-hardening`

## Code Shape Summary

The patch changes RPC parameter error handling in `core/src/rpc.rs`. The strongest grounded change is replacing an unchecked `bs58::decode(...).into_vec().unwrap()` in `deserialize_bs58_transaction` with fallible error propagation returning `InvalidParams`. Other changes reclassify oversized transactions, transaction deserialization failures, pubkey parse failures, and signature parse failures from `InvalidRequest` to `InvalidParams`. The evidence suppo...

## Search Motifs

- search for rpc input validation panic hardening checks near transaction-processing entrypoints
- compare validation before and after the input-shape-validation sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where RPC method execution, account scan, or transaction forwarding is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Replace unchecked decoding and generic request errors at the RPC boundary with fallible parameter validation that returns structured `InvalidParams` responses.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
