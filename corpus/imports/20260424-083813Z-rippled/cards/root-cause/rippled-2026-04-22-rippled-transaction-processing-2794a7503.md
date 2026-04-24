# Root-Cause Card

## Metadata

- ID: `rippled-2026-04-22-rippled-transaction-processing-2794a7503`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `invariant-check-state-overwrite`
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

- Primary impact: invariant-detection-bypass
- Secondary impact: Protocol-local correctness or hardening impact bounded by the reachable subsystem and surrounding checks.

## Short Reusable Lesson

- The patch fixes invariant detectors that previously overwrote stored boolean violation state for each visited ledger entry.
