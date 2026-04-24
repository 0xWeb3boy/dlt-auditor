# Root-Cause Card

## Metadata

- ID: `sui-2022-11-08-sui-storage-d8fef9cd19`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `ownership-invariant-enforcement`
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

- Primary impact: state-integrity
- Secondary impact: context-dependent

## Short Reusable Lesson

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. The patch changes Sui's native shared-object transfer path from an unconditional successful transfer record into a classified transfer result. `share_object` now rejects `OwnerChanged` with `E_SHARED_NON_NEW_OBJECT`, enforcing that non-new objects are not converted into shared ownership.
