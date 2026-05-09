# Code-Shape Card

## Metadata

- ID: `solana-2021-01-29-solana-transaction-processing-07cef5a557`
- Bug family: `authz_and_role_gates`
- Bug class: `authorization-invariant-enforcement`

## Code Shape Summary

The patch adds an on-chain authorization consistency check in Solana's upgradeable BPF loader. The loader now rejects deploy or upgrade processing when the buffer account's recorded authority does not match the supplied upgrade/deploy authority, and it prevents clearing buffer authority to None under the same feature gate.

## Search Motifs

- search for authorization invariant enforcement checks near transaction-processing entrypoints
- compare validation before and after the authorization-and-privilege-check sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for authority checks in wrappers but not at the final state-changing sink

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where account owner/write privilege, executable program state, or runtime syscall side effect is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Enforce the authority invariant at the on-chain loader boundary by comparing persisted buffer authority against the operation authority before continuing, and prevent state transitions that would remove the authority needed for that check.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The account or authority is derived from trusted state and cannot be chosen by the caller.
