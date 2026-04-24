# Root-Cause Card

## Metadata

- ID: `rippled-2026-04-21-rippled-transaction-processing-5ad05918f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-structural-validation`
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

- Primary impact: protocol-invariant-enforcement
- Secondary impact: Protocol-local correctness or hardening impact bounded by the reachable subsystem and surrounding checks.

## Short Reusable Lesson

- The patch fixes a validation gap for Permissioned DEX hybrid offers: the old invariant rejected missing sfAdditionalBooks and arrays larger than one, but did not reject an empty sfAdditionalBooks array when the field was present.
