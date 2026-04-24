# Root-Cause Card

## Metadata

- ID: `rippled-2022-06-22-rippled-transaction-processing-8266d9d59`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `negative-amount-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `numeric-bounds`

## Violated Invariant

- Invariant: Numeric protocol values must be range checked and rounded deterministically before they affect ledger accounting or eligibility decisions.

## Trust Boundary

- Boundary: untrusted transaction -> deterministic ledger state transition

## Attack Surface

- Entrypoint type: transaction-handler
- Sensitive sink: ledger state, balance/reserve accounting, or transaction authorization outcome

## Impact Pattern

- Primary impact: invalid-transaction-acceptance, protocol-invariant-enforcement
- Secondary impact: Protocol-local correctness or hardening impact bounded by the reachable subsystem and surrounding checks.

## Short Reusable Lesson

- The patch adds an amendment-gated rejection of negative NFT offer amounts in NFTokenCreateOffer::preflight.
