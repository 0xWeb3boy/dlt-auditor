# Code-Shape Card

## Metadata

- ID: `solana-2019-05-20-solana-transaction-processing-ead15d294e`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `panic-prone-input-parsing`

## Code Shape Summary

The grounded change is in core/src/rpc_pubsub.rs: account_subscribe, program_subscribe, and signature_subscribe replace direct bs58 decoding with unwrap() by fallible typed parameter parsing. This is plausibly defensive input handling, but the evidence does not prove a security vulnerability, whole-node crash, consensus impact, signature bypass, replay issue, or state corruption. The added get_epoch_vote_accounts RPC appears to be the main feature chang...

## Search Motifs

- search for panic prone input parsing checks near transaction-processing entrypoints
- compare validation before and after the input-shape-validation sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where RPC method execution, account scan, or transaction forwarding is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Replace direct unwrap-based parsing of external RPC parameters with fallible typed parsing before performing downstream subscription setup.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
