# Code-Shape Card

## Metadata

- ID: `solana-2021-09-08-solana-transaction-processing-38bbb77989`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `account-mutability-validation`

## Code Shape Summary

The patch tightens Solana runtime account-loading validation so transactions that request writable access to executable accounts or upgradeable-loader-owned accounts are rejected in the relevant loader-controlled cases. The evidence supports a security-relevant mutability invariant fix, but not stronger claims such as arbitrary code modification, consensus failure, or demonstrated state corruption.

## Search Motifs

- search for account mutability validation checks near transaction-processing entrypoints
- compare validation before and after the account-mutability-enforcement sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where account owner/write privilege, executable program state, or runtime syscall side effect is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Enforce account mutability invariants during transaction account loading, before execution, and fail transactions that request unauthorized writable access to executable or loader-managed program state.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
