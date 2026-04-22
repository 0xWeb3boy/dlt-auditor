# Root-Cause Card

## Metadata

- ID: `oasis-core-2024-05-11-oasis-core-core-logic-ddf51345a`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `integer-overflow`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `arithmetic-bounds`

## Violated Invariant

- Invariant: CHURP dealer construction must not silently wrap the derived Y-degree when computing 2 * threshold. If the doubled threshold is not representable in u8, construction should fail so the derived polynomial degree and verification-matrix dimensions stay consistent with the input threshold.

## Trust Boundary

- Boundary: `peer->node`

## Attack Surface

- Entrypoint type: `state-transition`
- Sensitive sink: `key-share release or secret-state acceptance`

## Impact Pattern

- Primary impact: `integrity-risk`
- Secondary impact: `none`

## Short Reusable Lesson

- CHURP dealer construction must not silently wrap the derived Y-degree when computing 2 * threshold. If the doubled threshold is not representable in u8, construction should fail so the derived polynomial degree and verification-matrix dimensions stay consistent with the input threshold. In this pattern, dealer::new used unchecked u8 arithmetic for a derived protocol parameter ('dy = 2 * threshold'), allowing overflow instead of rejecting an unrepresentable value. The robust fix is to make the privileged sink consume the canonical identity, state coordinate, or accounting result directly and to fail closed when that binding is missing.
