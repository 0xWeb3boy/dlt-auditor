# Root-Cause Card

## Metadata

- ID: `agave-2026-04-20-agave-transaction-processing-b9365a82f6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `transaction-sanitization-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `complete-transaction-structure-sanitization`

## Violated Invariant

- Invariant: A transaction view should be rejected at the sanitize boundary if size, signature counts, account limits, duplicate addresses, header fields, or config fields violate protocol bounds.

## Trust Boundary

- Boundary: `serialized-transaction->transaction-view`

## Attack Surface

- Entrypoint type: `transaction-sanitizer`
- Sensitive sink: sanitized transaction view exposed to downstream execution and verification
- Attacker capability: Submit serialized transactions with malformed headers, duplicate accounts, bad signature counts, oversized payloads, or invalid config fields.
- Key precondition: Malformed transaction views can be constructed before all structural invariants are checked.

## Impact Pattern

- Primary impact: `malformed-transaction-rejection`
- Secondary impact: `validation-hardening`
- Severity guidance: `low` because The patch strengthens a critical sanitizer, but the evidence did not prove a specific malformed transaction reached execution or caused consensus, fund, or availability impact.

## Short Reusable Lesson

- Transaction-view sanitization is split or incomplete, leaving version-specific size limits, signature/account consistency, duplicate-address rejection, and config/header checks unevenly enforced.
- Structural fix: Centralize sanitize flow and add explicit version-aware checks for size, signatures, accounts, duplicate addresses, headers, lookups, and config fields.
