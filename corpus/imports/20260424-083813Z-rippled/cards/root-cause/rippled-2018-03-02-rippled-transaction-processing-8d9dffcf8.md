# Root-Cause Card

## Metadata

- ID: `rippled-2018-03-02-rippled-transaction-processing-8d9dffcf8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `escrow-condition-validation-hardening`
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

- Primary impact: escrow-release-policy-hardening, economic-risk-reduction
- Secondary impact: Protocol-local correctness or hardening impact bounded by the reachable subsystem and surrounding checks.

## Short Reusable Lesson

- The patch changes XRP Ledger escrow creation and finish semantics under the fix1571 amendment.
