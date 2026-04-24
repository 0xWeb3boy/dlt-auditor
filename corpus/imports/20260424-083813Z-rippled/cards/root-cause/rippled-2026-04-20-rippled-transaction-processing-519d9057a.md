# Root-Cause Card

## Metadata

- ID: `rippled-2026-04-20-rippled-transaction-processing-519d9057a`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `invariant-enforcement`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-and-state-invariant-validation`

## Violated Invariant

- Invariant: Untrusted protocol input must satisfy structural, semantic, and state-dependent invariants before it is admitted to ledger, consensus, storage, or trust-management state.

## Trust Boundary

- Boundary: untrusted transaction -> deterministic ledger state transition

## Attack Surface

- Entrypoint type: transaction-handler
- Sensitive sink: ledger state, balance/reserve accounting, or transaction authorization outcome

## Impact Pattern

- Primary impact: ledger-integrity, permission-boundary-hardening
- Secondary impact: Protocol-local correctness or hardening impact bounded by the reachable subsystem and surrounding checks.

## Short Reusable Lesson

- The patch improves Permissioned Domain invariant checking in rippled by changing how affected Permissioned Domain ledger entries are recorded and finalized.
