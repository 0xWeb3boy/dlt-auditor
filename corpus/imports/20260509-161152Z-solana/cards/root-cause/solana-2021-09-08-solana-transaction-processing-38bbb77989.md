# Root-Cause Card

## Metadata

- ID: `solana-2021-09-08-solana-transaction-processing-38bbb77989`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `account-mutability-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `account-mutability-enforcement`

## Violated Invariant

- Protocol input must satisfy account mutability enforcement before it can reach account owner/write privilege, executable program state, or runtime syscall side effect.

## Trust Boundary

- Boundary: untrusted program instruction/CPI frame to runtime account and privilege enforcement

## Attack Surface

- Entrypoint type: native program, loader, SBF/BPF, or CPI invocation
- Sensitive sink: account owner/write privilege, executable program state, or runtime syscall side effect

## Root Cause

The account-loading validation around loader-managed program state was too narrow. The provided diff supports that writable handling was previously conditioned on executable upgradeable-loader-owned accounts, while the fix applies validation based on upgradeable-loader ownership and loader presence.

## Impact Pattern

- Primary impact: state-integrity
- Expected band: state_integrity_or_policy_bypass
- Severity guide: Low/Medium

## Short Reusable Lesson

The patch tightens Solana runtime account-loading validation so transactions that request writable access to executable accounts or upgradeable-loader-owned accounts are rejected in the relevant loader-controlled cases. The evidence supports a security-relevant mutability invariant fix, but not stronger claims such as arbitrary code modification, consensus failure, or demonstrated state corruption.
