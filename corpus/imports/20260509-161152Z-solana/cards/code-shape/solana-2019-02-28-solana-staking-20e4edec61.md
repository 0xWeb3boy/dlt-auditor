# Code-Shape Card

## Metadata

- ID: `solana-2019-02-28-solana-staking-20e4edec61`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `vote-account-binding-confusion`

## Code Shape Summary

The patch is plausibly security hardening for Solana vote account setup. The strongest evidence is the removed TODO in `sdk/src/vote_program.rs`, which explicitly warned that the old `register` flow assumed `keyed_accounts[0]` was the account creator for `keyed_accounts[1]` and that a different signed instruction in that slot could allow vote-account hijacking and leader-rotation insertion. The patch refactors the vote account setup path, adds explicit...

## Search Motifs

- search for vote account binding confusion checks near staking entrypoints
- compare validation before and after the stake-accountability-invariant sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where stake delegation, withdrawal, reward accounting, vote authority, or validator weight is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Replace implicit positional account assumptions with explicit signer and owner validation, while preserving vote account identity through runtime vote-state enumeration.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
