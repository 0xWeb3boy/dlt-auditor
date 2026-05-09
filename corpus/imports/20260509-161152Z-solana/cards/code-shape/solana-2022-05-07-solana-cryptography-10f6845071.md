# Code-Shape Card

## Metadata

- ID: `solana-2022-05-07-solana-cryptography-10f6845071`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-transaction-sanitization`

## Code Shape Summary

The patch changes versioned transaction sanitization to carry an explicit require_static_program_ids policy and makes the shown RPC transaction sanitization path pass true for that policy. This supports a likely security fix for rejecting v0 transactions where program dispatch identity depends on lookup-table-loaded addresses, but the provided snippets do not show the full v0 sanitizer or prove an exploit.

## Search Motifs

- search for improper transaction sanitization checks near cryptography entrypoints
- compare validation before and after the input-shape-validation sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where RPC method execution, account scan, or transaction forwarding is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Thread an explicit validation policy through transaction/message sanitization and set it at the boundary that creates sanitized transaction representations.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
