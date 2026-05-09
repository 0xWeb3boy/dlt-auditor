# Root-Cause Card

## Metadata

- ID: `solana-2020-11-16-solana-staking-e12cb457fb`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `account-owner-validation`
- Confidence tier: `tier_b_likely`

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

Stake-management code lacked explicit owner validation for some account parameters before interpreting them according to stake or vote account roles.

## Impact Pattern

- Primary impact: state-integrity
- Expected band: state_integrity_or_policy_bypass
- Severity guide: Low/Medium

## Short Reusable Lesson

The patch adds explicit owner checks to Solana stake-management paths so delegate, split, and merge reject wrong-owner stake or vote account inputs with `InstructionError::IncorrectProgramId`. The commit subject and runtime guard changes support classifying this as an account-owner-validation security fix.
