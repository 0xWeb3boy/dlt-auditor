# Code-Shape Card

## Metadata

- ID: `solana-2021-09-02-solana-validator-ops-e288459cf2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unsafe-authority-default`

## Code Shape Summary

The patch hardens Solana's create-vote-account CLI path by making `authorized_withdrawer` required and removing the previous fallback that used the validator identity key when the argument was omitted. The provided code also shows a new parser-side rejection when the authorized withdrawer equals the vote account pubkey unless `--allow-unsafe-authorized-withdrawer` is supplied.

## Search Motifs

- search for unsafe authority default checks near validator-ops entrypoints
- compare validation before and after the authorization-and-privilege-check sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for authority checks in wrappers but not at the final state-changing sink

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where stake delegation, withdrawal, reward accounting, vote authority, or validator weight is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Require explicit configuration for a security-sensitive authority, remove unsafe implicit defaults, and add parser-level key-separation checks with an explicit unsafe override.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The account or authority is derived from trusted state and cannot be chosen by the caller.
