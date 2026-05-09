# Code-Shape Card

## Metadata

- ID: `solana-2022-09-22-solana-transaction-processing-565aacc23a`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-account-mutability-check`

## Code Shape Summary

The patch likely hardens Solana's upgradeable BPF loader by changing the extension flow from a ProgramData-centered instruction to a Program-centered instruction and adding a runtime check that rejects the operation when the Program account is not writable. The evidence supports a missing writable-account enforcement issue, but does not establish a concrete exploit such as arbitrary ProgramData modification or privilege escalation.

## Search Motifs

- search for missing account mutability check checks near transaction-processing entrypoints
- compare validation before and after the account-mutability-enforcement sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where account owner/write privilege, executable program state, or runtime syscall side effect is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Add explicit account metadata validation in the runtime loader before continuing with executable data extension, and align client/parser instruction semantics with the stricter account model.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
