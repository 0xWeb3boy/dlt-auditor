# Root-Cause Card

## Metadata

- ID: `solana-2021-06-06-solana-transaction-processing-e5ea16fad8`
- Bug family: `authz_and_role_gates`
- Bug class: `authorization-check-bypass`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `signature-and-signer-binding`

## Violated Invariant

- Protocol input must satisfy signature and signer binding before it can reach account owner/write privilege, executable program state, or runtime syscall side effect.

## Trust Boundary

- Boundary: untrusted program instruction/CPI frame to runtime account and privilege enforcement

## Attack Surface

- Entrypoint type: native program, loader, SBF/BPF, or CPI invocation
- Sensitive sink: account owner/write privilege, executable program state, or runtime syscall side effect

## Root Cause

A zero-value fast path in the System Program transfer handler was placed before source-account authorization, allowing the zero-lamport case to skip the signer requirement enforced for nonzero transfers.

## Impact Pattern

- Primary impact: authorization-bypass
- Expected band: defense_in_depth_or_input_hardening
- Severity guide: High

## Short Reusable Lesson

The supported finding is limited to an authorization check gap in zero-lamport System Program transfers. Before the patch, `transfer` returned `Ok(())` for `lamports == 0` before checking whether the source account signed. After the patch, that legacy early return is gated behind `!system_transfer_zero_check`, so when the feature is active the existing missing-signature check runs and unsigned zero-lamport transfers fail.
