# Code-Shape Card

## Metadata

- ID: `snarkvm-2025-06-24-snarkvm-consensus-638f5f69c`
- Bug family: `authz_and_role_gates`
- Bug class: `reserved-locator-validation-hardening`

## Code Shape Summary

- A deployment verifier checked for a reserved locator only inside a narrower gated path, leaving the invariant less explicit than the reserved call semantics required.

## Search Motifs

- program contains locator credits.aleo/upgrade
- reserved system function check nested under consensus version gate
- deployment verifier distinguishes direct user call from program-mediated call

## Typical Asymmetry

- The code accepted or derived security-sensitive state before proving the boundary property named in the record: `reserved-entrypoint-gating`.

## Patch Pattern

- Name the reserved-locator invariant and invoke it directly during deployment verification outside the prior narrow gate.

## False Match Warnings

- The reserved function performs its own caller authorization for all indirect calls.
- The deployment format cannot encode the reserved locator in executable code.
- A broader verifier already rejects the same locator before this check.
