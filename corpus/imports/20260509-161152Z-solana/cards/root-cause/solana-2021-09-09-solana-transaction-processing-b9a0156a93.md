# Root-Cause Card

## Metadata

- ID: `solana-2021-09-09-solana-transaction-processing-b9a0156a93`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-writable-account-validation`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `authorization-and-privilege-check`

## Violated Invariant

- Protocol input must satisfy authorization and privilege check before it can reach account owner/write privilege, executable program state, or runtime syscall side effect.

## Trust Boundary

- Boundary: untrusted program instruction/CPI frame to runtime account and privilege enforcement

## Attack Surface

- Entrypoint type: native program, loader, SBF/BPF, or CPI invocation
- Sensitive sink: account owner/write privilege, executable program state, or runtime syscall side effect

## Root Cause

The prior validation was scoped too narrowly to executable upgradeable-loader-owned accounts. Based on the commit message and diff, some upgradeable-loader-owned program state such as ProgramData accounts could be treated as writable in transaction loading when the upgradeable loader was not present.

## Impact Pattern

- Primary impact: state-integrity, access-control
- Expected band: state_integrity_or_policy_bypass
- Severity guide: Medium

## Short Reusable Lesson

The patch tightens Solana runtime account loading so writable executable accounts and upgradeable-loader-owned ProgramData/state accounts are rejected when the upgradeable loader is not present. The evidence supports a transaction validation and account access-control fix, but does not establish arbitrary code execution, unauthorized upgrade, or consensus divergence.
