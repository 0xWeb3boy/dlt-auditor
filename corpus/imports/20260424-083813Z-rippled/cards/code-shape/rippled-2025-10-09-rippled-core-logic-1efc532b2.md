# Code-Shape Card

## Metadata

- ID: `rippled-2025-10-09-rippled-core-logic-1efc532b2`
- Bug family: `authz_and_role_gates`
- Bug class: `receiver-authorization-hardening`

## Code Shape Summary

- The provided evidence shows changes in LoanSet and LoanPay around amortization validation, borrower holding creation, vault receipt authorization, and broker-fee routing when freeze/deep-freeze state affects the intended receiver. Reusable shape: check for authorization was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: authorization-check-path missing exact authorization check before privileged account action, delegated permission, or role-scoped state change
- Motif 2: security-sensitive path reaches privileged account action, delegated permission, or role-scoped state change before rejecting malformed, stale, or unauthorized input
- Motif 3: Add explicit eligibility checks and guarded side effects in lending transaction paths: validate amortization inputs, limit automatic holding creation in the shown path, require authorization before vault receipt, and route broker fees according to...

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into privileged account action, delegated permission, or role-scoped state change unless the authorization gate runs before the state-changing branch.

## Patch Pattern

- Add explicit eligibility checks and guarded side effects in lending transaction paths: validate amortization inputs, limit automatic holding creation in the shown path, require authorization before vault receipt, and route broker fees according to...

## False Match Warnings

- No exploit scenario or attacker-controlled transaction sequence is provided.
- No evidence shows that the old behavior was reachable in a released configuration.
