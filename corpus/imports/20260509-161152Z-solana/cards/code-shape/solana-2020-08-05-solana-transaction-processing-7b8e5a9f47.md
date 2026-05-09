# Code-Shape Card

## Metadata

- ID: `solana-2020-08-05-solana-transaction-processing-7b8e5a9f47`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-transaction-sanitization`

## Code Shape Summary

The patch adds transaction sanitization to Solana RPC preflight simulation batch preparation. The evidence supports a missing validation fix for malformed transaction structure, specifically an invalid program_id_index in a preflight test. It does not establish an exploitable security vulnerability or concrete impact beyond clean rejection of malformed input.

## Search Motifs

- search for missing transaction sanitization checks near transaction-processing entrypoints
- compare validation before and after the input-shape-validation sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where RPC method execution, account scan, or transaction forwarding is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Run structural validation at the RPC preflight simulation batch boundary and propagate validation failures through the existing transaction error type.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
