# Root-Cause Card

## Metadata

- ID: `solana-2021-01-19-solana-cryptography-540e23c987`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `account-locking-invariant`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-shape-validation`

## Violated Invariant

- Protocol input must satisfy input shape validation before it can reach account owner/write privilege, executable program state, or runtime syscall side effect.

## Trust Boundary

- Boundary: untrusted program instruction/CPI frame to runtime account and privilege enforcement

## Attack Surface

- Entrypoint type: native program, loader, SBF/BPF, or CPI invocation
- Sensitive sink: account owner/write privilege, executable program state, or runtime syscall side effect

## Root Cause

The upgrade path did not require the executable program account itself to be writable, so an Upgrade instruction could be represented as only a read reference to the program account. That weakened the account-locking signal needed to conflict with simultaneous or same-batch invocation.

## Impact Pattern

- Primary impact: runtime-integrity
- Expected band: integrity_or_funds
- Severity guide: High

## Short Reusable Lesson

The patch hardens Solana's upgradeable BPF loader by requiring the executable program account to be writable during Upgrade processing and by changing the SDK Upgrade instruction builder to mark that account writable. This supports the stated goal of preventing program invocation and upgrade in the same transaction batch. The evidence supports account-locking and loader hardening, not unauthorized upgrade, signature bypass, replay, or cryptographic fail...
