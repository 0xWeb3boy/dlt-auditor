# Root-Cause Card

## Metadata

- ID: `sui-2026-03-23-sui-storage-7c7e923e6b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incorrect-owner-resolution`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `authorization`

## Violated Invariant

- Invariant: Object ownership and access checks must be enforced before a transaction can read, mutate, or consume object state.

## Trust Boundary

- Boundary: executed effects or checkpoint data -> authenticated persistent state

## Attack Surface

- Entrypoint type: state-transition-storage-update
- Sensitive sink: authorizing object access or privileged state mutation

## Impact Pattern

- Primary impact: policy-enforcement
- Secondary impact: access-control

## Short Reusable Lesson

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. The patch changes coin deny-list v2 owner extraction for written coin objects so that, under a new `use_coin_party_owner` protocol flag, it uses `object.owner.get_owner_address()` instead of always using `get_address_owner_address()`.
