# Code-Shape Card

## Metadata

- ID: `solana-2021-01-29-solana-transaction-processing-08bda35fd6`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`

## Code Shape Summary

The patch adds a feature-gated authority-equivalence check in the upgradeable BPF loader. Previously the loader verified that the supplied account was a Buffer but ignored its authority_address in the shown deploy/upgrade verification path. After the patch, mismatched buffer and upgrade authorities fail with IncorrectAuthority, and buffer authority removal is rejected under the same feature gate.

## Search Motifs

- search for access control checks near transaction-processing entrypoints
- compare validation before and after the authorization-and-privilege-check sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for authority checks in wrappers but not at the final state-changing sink

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where account owner/write privilege, executable program state, or runtime syscall side effect is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Add an explicit feature-gated authorization invariant in the loader path, then prevent state transitions that would bypass or make that invariant impossible to evaluate.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The account or authority is derived from trusted state and cannot be chosen by the caller.
