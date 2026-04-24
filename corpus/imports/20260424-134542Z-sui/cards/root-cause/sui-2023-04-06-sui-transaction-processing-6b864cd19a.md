# Root-Cause Card

## Metadata

- ID: `sui-2023-04-06-sui-transaction-processing-6b864cd19a`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incomplete-ownership-validation`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `authorization`

## Violated Invariant

- Invariant: Object ownership and access checks must be enforced before a transaction can read, mutate, or consume object state.

## Trust Boundary

- Boundary: submitted transaction or validator response -> execution/effects pipeline

## Attack Surface

- Entrypoint type: transaction-handler
- Sensitive sink: authorizing object access or privileged state mutation

## Impact Pattern

- Primary impact: state-integrity
- Secondary impact: context-dependent

## Short Reusable Lesson

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. The patch fixes an incomplete gas-object ownership check in Sui transaction validation. Previously, only the primary gas object was required to have `Owner::AddressOwner`; additional gas objects in `more_gas_objs` were not checked by the same validation.
