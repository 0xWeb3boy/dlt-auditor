# Code-Shape Card

## Metadata

- ID: `solana-2021-10-26-solana-staking-4fe3354c8f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unchecked-sysvar-account-input`

## Code Shape Summary

The patch adds safer Solana instructions-sysvar helper APIs and updates an example caller to use one of them. The evidence supports security-relevant hardening around sysvar identity checks and relative instruction lookup error handling, but not a confirmed vulnerability fix.

## Search Motifs

- search for unchecked sysvar account input checks near staking entrypoints
- compare validation before and after the input-shape-validation sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where account balance/state mutation, fee/rent accounting, nonce state, or transaction commitment is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Add checked SDK helper APIs that accept AccountInfo, validate the expected sysvar id before reading, return typed ProgramError values for invalid inputs, and add regression tests for boundary behavior.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
