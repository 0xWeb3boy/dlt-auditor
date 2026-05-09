# Root-Cause Card

## Metadata

- ID: `solana-2021-01-23-solana-cryptography-480a35d678`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-privilege-propagation`
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

The supported root cause is missing or insufficient propagation of effective writable privilege into account verification, especially for CPI paths where caller privileges may differ from callee message metadata. The exact rejected mutation condition is not shown in the provided evidence because the full `PreAccount::verify` implementation is absent.

## Impact Pattern

- Primary impact: state-integrity
- Expected band: state_integrity_or_policy_bypass
- Severity guide: Low/Medium

## Short Reusable Lesson

The patch adds tracking for account writable deescalation in Solana runtime/BPF CPI execution. The strongest supported claim is that writable privilege context is now threaded into post-instruction account verification paths so account changes can be checked against the caller-effective writable status.
