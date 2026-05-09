# Code-Shape Card

## Metadata

- ID: `solana-2020-05-26-solana-storage-8c8e2c4b2b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `cross-program-invocation-privilege-escalation`

## Code Shape Summary

The patch is a security fix for privilege escalation in Solana's BPF cross-program invocation path. The grounded evidence shows a new `verify_instruction` check in `programs/bpf_loader/src/syscalls.rs`, a call to that verification before callee message construction, and VM setup changed to pass caller parameter accounts so the syscall layer has the account privilege context needed for the check.

## Search Motifs

- search for cross program invocation privilege escalation checks near storage entrypoints
- compare validation before and after the authorization-and-privilege-check sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for authority checks in wrappers but not at the final state-changing sink

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where canonical bank state, account storage, snapshot acceptance, or ledger root is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Add pre-dispatch privilege validation at the BPF CPI syscall boundary and thread caller account context into the VM/syscall layer.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The account or authority is derived from trusted state and cannot be chosen by the caller.
