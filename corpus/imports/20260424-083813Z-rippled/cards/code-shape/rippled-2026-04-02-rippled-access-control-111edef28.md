# Code-Shape Card

## Metadata

- ID: `rippled-2026-04-02-rippled-access-control-111edef28`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `ledger-accounting-invariant`

## Code Shape Summary

- The supported finding is a lending LoanBroker accounting-invariant hardening, not an access-control flaw or proven funds-theft vulnerability. Reusable shape: check for accounting-integrity was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: authorization-check-path missing exact accounting-integrity check before privileged account action, delegated permission, or role-scoped state change
- Motif 2: security-sensitive path reaches privileged account action, delegated permission, or role-scoped state change before rejecting malformed, stale, or unauthorized input
- Motif 3: Compute the authoritative accounting baseline once and enforce both sides of the consistency invariant, with an explicit exception for a documented deletion lifecycle case.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into privileged account action, delegated permission, or role-scoped state change unless the accounting-integrity gate runs before the state-changing branch.

## Patch Pattern

- Compute the authoritative accounting baseline once and enforce both sides of the consistency invariant, with an explicit exception for a documented deletion lifecycle case.

## False Match Warnings

- No transaction sequence is shown that can create an excessive sfCoverAvailable value before the fix.
- No exploit path, funds theft, signature bypass, or privilege escalation is demonstrated.
