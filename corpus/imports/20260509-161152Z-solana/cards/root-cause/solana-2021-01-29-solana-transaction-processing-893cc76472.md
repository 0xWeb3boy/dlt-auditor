# Root-Cause Card

## Metadata

- ID: `solana-2021-01-29-solana-transaction-processing-893cc76472`
- Bug family: `authz_and_role_gates`
- Bug class: `authorization-invariant-bypass`
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

The loader parsed buffer authority state but did not enforce that the buffer authority matched the program upgrade authority in the deploy/upgrade path. This allowed a buffer controlled by a different authority to be accepted for the observed operation before the new feature-gated check.

## Impact Pattern

- Primary impact: authorization-integrity
- Expected band: defense_in_depth_or_input_hardening
- Severity guide: Low/Medium

## Short Reusable Lesson

The patch strengthens upgradeable BPF loader authorization by requiring the buffer authority to match the upgrade authority for deploy and upgrade operations under the matching_buffer_upgrade_authorities feature. It also prevents setting buffer authority to None under the same feature and updates CLI behavior and tests around that invariant.
