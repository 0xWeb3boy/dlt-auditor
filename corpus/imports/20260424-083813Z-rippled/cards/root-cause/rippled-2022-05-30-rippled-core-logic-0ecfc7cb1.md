# Root-Cause Card

## Metadata

- ID: `rippled-2022-05-30-rippled-core-logic-0ecfc7cb1`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `hardening-or-correctness-fix`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: Untrusted protocol input must satisfy structural, semantic, and state-dependent invariants before it is admitted to ledger, consensus, storage, or trust-management state.

## Trust Boundary

- Boundary: protocol-controlled input -> core ledger/application invariant

## Attack Surface

- Entrypoint type: state-transition-or-core-validation-path
- Sensitive sink: ledger invariant, protocol state, or node safety decision

## Impact Pattern

- Primary impact: correctness-or-hardening
- Secondary impact: Protocol-local correctness or hardening impact bounded by the reachable subsystem and surrounding checks.

## Short Reusable Lesson

- This is best treated as TLS/SSL context hardening in rippled, not a confirmed vulnerability fix.
