# Root-Cause Card

## Metadata

- ID: `firedancer-2025-10-01-firedancer-transaction-processing-63751c1d6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `race-condition`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `slot-scoped-state-snapshot-binding`

## Violated Invariant

- Invariant: State lookups must bind to the exact slot or transaction snapshot they intend to observe, and fail closed if that snapshot is unavailable.

## Trust Boundary

- Boundary: Concurrent replay and bank state crossing into address lookup table resolution.

## Attack Surface

- Entrypoint type: address lookup table resolution path
- Sensitive sink: address lookup against mutable shared state

## Impact Pattern

- Primary impact: state integrity
- Secondary impact: availability

## Short Reusable Lesson

- The lookup path relied on a root or null transaction context even though replay could swap the underlying state before the address table read completed.
