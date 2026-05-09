# Code-Shape Card

## Metadata

- ID: `solana-2021-09-09-solana-transaction-processing-b9a0156a93`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-writable-account-validation`

## Code Shape Summary

The patch tightens Solana runtime account loading so writable executable accounts and upgradeable-loader-owned ProgramData/state accounts are rejected when the upgradeable loader is not present. The evidence supports a transaction validation and account access-control fix, but does not establish arbitrary code execution, unauthorized upgrade, or consensus divergence.

## Search Motifs

- search for improper writable account validation checks near transaction-processing entrypoints
- compare validation before and after the authorization-and-privilege-check sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for authority checks in wrappers but not at the final state-changing sink

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where account owner/write privilege, executable program state, or runtime syscall side effect is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Enforce the writable-account invariant during transaction account loading, using ownership and transaction context rather than executable status alone, and add explicit error accounting and regression coverage.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The account or authority is derived from trusted state and cannot be chosen by the caller.
