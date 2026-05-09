# Code-Shape Card

## Metadata

- ID: `solana-2021-09-02-solana-validator-ops-afb87a386a`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unsafe-key-reuse`

## Code Shape Summary

The patch hardens Solana CLI vote account creation by making `authorized_withdrawer` a required concrete pubkey instead of an optional value that defaulted to the validator identity. It also adds an unsafe-configuration override flag and, in the shown evidence, rejects the authorized withdrawer being identical to the vote account pubkey unless that override is used.

## Search Motifs

- search for unsafe key reuse checks near validator-ops entrypoints
- compare validation before and after the stake-accountability-invariant sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where stake delegation, withdrawal, reward accounting, vote authority, or validator weight is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Require explicit input for a security-sensitive authority, remove implicit defaulting to operational keys, and gate known unsafe key reuse behind an explicit unsafe override.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
