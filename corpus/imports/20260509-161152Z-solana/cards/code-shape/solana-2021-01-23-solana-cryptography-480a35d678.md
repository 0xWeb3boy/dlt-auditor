# Code-Shape Card

## Metadata

- ID: `solana-2021-01-23-solana-cryptography-480a35d678`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-privilege-propagation`

## Code Shape Summary

The patch adds tracking for account writable deescalation in Solana runtime/BPF CPI execution. The strongest supported claim is that writable privilege context is now threaded into post-instruction account verification paths so account changes can be checked against the caller-effective writable status.

## Search Motifs

- search for improper privilege propagation checks near cryptography entrypoints
- compare validation before and after the authorization-and-privilege-check sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for authority checks in wrappers but not at the final state-changing sink

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where account owner/write privilege, executable program state, or runtime syscall side effect is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Propagate effective authorization state across the CPI/runtime boundary and use it during post-instruction account verification.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The account or authority is derived from trusted state and cannot be chosen by the caller.
