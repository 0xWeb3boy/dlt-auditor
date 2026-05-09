# Code-Shape Card

## Metadata

- ID: `solana-2020-12-17-solana-cryptography-ff728e5e56`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `rent-exemption-undercheck`

## Code Shape Summary

The patch fixes an undercheck in Solana's upgradeable BPF loader deploy path. Previously, the Program account rent-exemption check used the fixed `UpgradeableLoaderState::program_len()` size, even when the account's actual `data_len()` was larger. The patched code separately rejects accounts that are too small, then requires rent exemption based on `program.data_len()`.

## Search Motifs

- search for rent exemption undercheck checks near cryptography entrypoints
- compare validation before and after the rent-exemption-invariant sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where account owner/write privilege, executable program state, or runtime syscall side effect is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Separate minimum layout validation from economic/accounting validation, and compute rent exemption from the actual account allocation.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
