# Code-Shape Card

## Metadata

- ID: `solana-2021-09-09-solana-transaction-processing-3eee222667`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-writable-account-validation`

## Code Shape Summary

The patch tightens Solana runtime account loading by rejecting writable locks on upgradeable-loader-owned program accounts when the upgradeable loader is not present. The evidence supports a security-relevant runtime invariant around protected program state, but it does not prove a complete exploit or unauthorized mutation path, so the verdict is downgraded from confirmed to likely security hardening.

## Search Motifs

- search for improper writable account validation checks near transaction-processing entrypoints
- compare validation before and after the account-mutability-enforcement sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where account owner/write privilege, executable program state, or runtime syscall side effect is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Broaden transaction-load-time validation for protected program-state accounts and reject invalid writable locks before execution.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
