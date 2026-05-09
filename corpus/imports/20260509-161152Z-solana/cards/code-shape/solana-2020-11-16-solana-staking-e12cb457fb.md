# Code-Shape Card

## Metadata

- ID: `solana-2020-11-16-solana-staking-e12cb457fb`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `account-owner-validation`

## Code Shape Summary

The patch adds explicit owner checks to Solana stake-management paths so delegate, split, and merge reject wrong-owner stake or vote account inputs with `InstructionError::IncorrectProgramId`. The commit subject and runtime guard changes support classifying this as an account-owner-validation security fix.

## Search Motifs

- search for account owner validation checks near staking entrypoints
- compare validation before and after the authorization-and-privilege-check sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for authority checks in wrappers but not at the final state-changing sink

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where account owner/write privilege, executable program state, or runtime syscall side effect is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Validate account owner program at the instruction boundary before interpreting account state or continuing stake-management logic.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The account or authority is derived from trusted state and cannot be chosen by the caller.
