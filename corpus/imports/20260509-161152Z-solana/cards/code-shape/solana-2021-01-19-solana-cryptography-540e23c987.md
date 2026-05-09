# Code-Shape Card

## Metadata

- ID: `solana-2021-01-19-solana-cryptography-540e23c987`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `account-locking-invariant`

## Code Shape Summary

The patch hardens Solana's upgradeable BPF loader by requiring the executable program account to be writable during Upgrade processing and by changing the SDK Upgrade instruction builder to mark that account writable. This supports the stated goal of preventing program invocation and upgrade in the same transaction batch. The evidence supports account-locking and loader hardening, not unauthorized upgrade, signature bypass, replay, or cryptographic fail...

## Search Motifs

- search for account locking invariant checks near cryptography entrypoints
- compare validation before and after the input-shape-validation sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where account owner/write privilege, executable program state, or runtime syscall side effect is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Mark the execution-bearing program account writable for upgrade instructions and enforce the same requirement in the loader under a feature gate.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
