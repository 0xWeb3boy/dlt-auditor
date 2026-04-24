# Root-Cause Card

## Metadata

- ID: `rippled-2025-04-11-rippled-transaction-processing-da10ba6fd`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `ledger-state-integrity`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: Untrusted protocol input must satisfy structural, semantic, and state-dependent invariants before it is admitted to ledger, consensus, storage, or trust-management state.

## Trust Boundary

- Boundary: untrusted transaction -> deterministic ledger state transition

## Attack Surface

- Entrypoint type: transaction-handler
- Sensitive sink: ledger state, balance/reserve accounting, or transaction authorization outcome

## Impact Pattern

- Primary impact: ledger-integrity
- Secondary impact: Protocol-local correctness or hardening impact bounded by the reachable subsystem and surrounding checks.

## Short Reusable Lesson

- The supported finding is a ledger-state integrity fix in LoanBrokerDelete, not an access-control fix.
