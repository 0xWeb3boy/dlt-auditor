# Root-Cause Card

## Metadata

- ID: `oasis-core-2020-01-31-oasis-core-staking-956168c04`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `integer-overflow`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `arithmetic-bounds`

## Violated Invariant

- Invariant: When duplicate-vote evidence is processed, the recorded validator freeze end time should preserve the configured penalty and must not wrap if 'epoch + FreezeInterval' exceeds the representable epoch range.

## Trust Boundary

- Boundary: `validator->consensus`

## Attack Surface

- Entrypoint type: `state-transition`
- Sensitive sink: `validator penalty state`

## Impact Pattern

- Primary impact: `integrity`
- Secondary impact: `none`

## Short Reusable Lesson

- When duplicate-vote evidence is processed, the recorded validator freeze end time should preserve the configured penalty and must not wrap if 'epoch + FreezeInterval' exceeds the representable epoch range. In this pattern, unchecked integer addition when deriving 'nodeStatus.FreezeEndTime' from the current epoch and the configured freeze interval. The robust fix is to make the privileged sink consume the canonical identity, state coordinate, or accounting result directly and to fail closed when that binding is missing.
