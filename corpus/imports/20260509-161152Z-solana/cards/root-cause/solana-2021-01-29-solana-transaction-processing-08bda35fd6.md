# Root-Cause Card

## Metadata

- ID: `solana-2021-01-29-solana-transaction-processing-08bda35fd6`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`
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

The loader authorization check was incomplete: it validated the account state as Buffer but did not enforce that the Buffer authority matched the upgrade authority for deploy/upgrade processing. That allowed the operation to proceed past the shown check with a Buffer controlled by a different authority.

## Impact Pattern

- Primary impact: state-integrity
- Expected band: state_integrity_or_policy_bypass
- Severity guide: Medium

## Short Reusable Lesson

The patch adds a feature-gated authority-equivalence check in the upgradeable BPF loader. Previously the loader verified that the supplied account was a Buffer but ignored its authority_address in the shown deploy/upgrade verification path. After the patch, mismatched buffer and upgrade authorities fail with IncorrectAuthority, and buffer authority removal is rejected under the same feature gate.
