# Root-Cause Card

## Metadata

- ID: `solana-2021-09-09-solana-transaction-processing-3eee222667`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-writable-account-validation`
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

Transaction account-loading validation was too narrowly scoped around executable upgradeable-loader-owned accounts, rather than consistently rejecting ordinary writable locks on upgradeable-loader-owned program state when the loader-mediated path was absent.

## Impact Pattern

- Primary impact: state-integrity
- Expected band: state_integrity_or_policy_bypass
- Severity guide: Low/Medium

## Short Reusable Lesson

The patch tightens Solana runtime account loading by rejecting writable locks on upgradeable-loader-owned program accounts when the upgradeable loader is not present. The evidence supports a security-relevant runtime invariant around protected program state, but it does not prove a complete exploit or unauthorized mutation path, so the verdict is downgraded from confirmed to likely security hardening.
