# Root-Cause Card

## Metadata

- ID: `solana-2021-01-29-solana-transaction-processing-07cef5a557`
- Bug family: `authz_and_role_gates`
- Bug class: `authorization-invariant-enforcement`
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

The upgradeable loader accepted a buffer based on its account state without enforcing that the buffer's stored authority matched the authority used for the sensitive deploy or upgrade operation. The related ability to clear buffer authority to None would also make the new comparison unenforceable, so the patch blocks that state under the feature gate.

## Impact Pattern

- Primary impact: access-control, state-integrity
- Expected band: state_integrity_or_policy_bypass
- Severity guide: Medium

## Short Reusable Lesson

The patch adds an on-chain authorization consistency check in Solana's upgradeable BPF loader. The loader now rejects deploy or upgrade processing when the buffer account's recorded authority does not match the supplied upgrade/deploy authority, and it prevents clearing buffer authority to None under the same feature gate.
