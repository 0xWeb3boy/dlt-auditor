# Root-Cause Card

## Metadata

- ID: `solana-2020-12-17-solana-cryptography-ff728e5e56`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `rent-exemption-undercheck`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `rent-exemption-invariant`

## Violated Invariant

- Protocol input must satisfy rent exemption invariant before it can reach account owner/write privilege, executable program state, or runtime syscall side effect.

## Trust Boundary

- Boundary: untrusted program instruction/CPI frame to runtime account and privilege enforcement

## Attack Surface

- Entrypoint type: native program, loader, SBF/BPF, or CPI invocation
- Sensitive sink: account owner/write privilege, executable program state, or runtime syscall side effect

## Root Cause

The deploy path conflated the minimum structural size of a Program account with the size that should be used for rent accounting. It checked rent against `UpgradeableLoaderState::program_len()` instead of the Program account's actual `data_len()`.

## Impact Pattern

- Primary impact: economic-invariant
- Expected band: integrity_or_funds
- Severity guide: Low/Medium

## Short Reusable Lesson

The patch fixes an undercheck in Solana's upgradeable BPF loader deploy path. Previously, the Program account rent-exemption check used the fixed `UpgradeableLoaderState::program_len()` size, even when the account's actual `data_len()` was larger. The patched code separately rejects accounts that are too small, then requires rent exemption based on `program.data_len()`.
