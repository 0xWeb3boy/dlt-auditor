# Code-Shape Card

## Metadata

- ID: `rippled-2026-04-03-rippled-access-control-c0ee81366`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `ledger-accounting-invariant`

## Code Shape Summary

- The best-supported finding is a Lending Protocol loan-broker accounting invariant hardening. Reusable shape: check for accounting-integrity was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: authorization-check-path missing exact accounting-integrity check before privileged account action, delegated permission, or role-scoped state change
- Motif 2: security-sensitive path reaches privileged account action, delegated permission, or role-scoped state change before rejecting malformed, stale, or unauthorized input
- Motif 3: Tighten a protocol ledger invariant from a one-sided bound to an amendment-gated consistency check, while preserving a documented lifecycle exception for deletion.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into privileged account action, delegated permission, or role-scoped state change unless the accounting-integrity gate runs before the state-changing branch.

## Patch Pattern

- Tighten a protocol ledger invariant from a one-sided bound to an amendment-gated consistency check, while preserving a documented lifecycle exception for deletion.

## False Match Warnings

- No proof of how invalid sfCoverAvailable state could be created by an attacker.
- No demonstrated authorization bypass, signer bug, or role-check failure.
