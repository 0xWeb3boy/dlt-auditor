# Code-Shape Card

## Metadata

- ID: `rippled-2026-04-03-rippled-access-control-c979643d0`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `accounting-invariant`

## Code Shape Summary

- The patch adds an amendment-gated LoanBroker accounting invariant and makes adjacent lending protocol adjustments. Reusable shape: check for accounting-integrity was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: authorization-check-path missing exact accounting-integrity check before privileged account action, delegated permission, or role-scoped state change
- Motif 2: security-sensitive path reaches privileged account action, delegated permission, or role-scoped state change before rejecting malformed, stale, or unauthorized input
- Motif 3: Add an amendment-gated invariant check for the missing side of an accounting relationship, while preserving an explicitly documented exceptional transaction case and aligning nearby lending protocol behavior.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into privileged account action, delegated permission, or role-scoped state change unless the accounting-integrity gate runs before the state-changing branch.

## Patch Pattern

- Add an amendment-gated invariant check for the missing side of an accounting relationship, while preserving an explicitly documented exceptional transaction case and aligning nearby lending protocol behavior.

## False Match Warnings

- No advisory or security note is provided.
- No exploit sequence shows how an invalid LoanBroker state could be created.
