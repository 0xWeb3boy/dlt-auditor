# Code-Shape Card

## Metadata

- ID: `solana-2020-05-26-solana-storage-03abd3ddd7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-privilege-check`

## Code Shape Summary

Commit 03abd3ddd7 is supported as a security fix for Solana's BPF cross-program invocation path. The strongest evidence is the new verify_instruction helper in programs/bpf_loader/src/syscalls.rs, explicitly introduced with a privilege-escalation check and invoked before Message construction and dispatch.

## Search Motifs

- search for missing privilege check checks near storage entrypoints
- compare validation before and after the authorization-and-privilege-check sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for authority checks in wrappers but not at the final state-changing sink

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where canonical bank state, account storage, snapshot acceptance, or ledger root is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Add a pre-dispatch privilege validation gate at the BPF CPI syscall boundary.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The account or authority is derived from trusted state and cannot be chosen by the caller.
