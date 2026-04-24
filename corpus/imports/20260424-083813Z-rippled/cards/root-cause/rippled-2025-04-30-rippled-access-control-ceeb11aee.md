# Root-Cause Card

## Metadata

- ID: `rippled-2025-04-30-rippled-access-control-ceeb11aee`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `ledger-state-invariant-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-and-state-invariant-validation`

## Violated Invariant

- Invariant: Untrusted protocol input must satisfy structural, semantic, and state-dependent invariants before it is admitted to ledger, consensus, storage, or trust-management state.

## Trust Boundary

- Boundary: externally submitted action -> account, delegate, or role authorization gate

## Attack Surface

- Entrypoint type: authorization-check-path
- Sensitive sink: privileged account action, delegated permission, or role-scoped state change

## Impact Pattern

- Primary impact: ledger-state-integrity
- Secondary impact: Protocol-local correctness or hardening impact bounded by the reachable subsystem and surrounding checks.

## Short Reusable Lesson

- The patch strengthens an AccountRoot deletion invariant in rippled by adding a check that a deleted account must not have a non-zero owner count.
