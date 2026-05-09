# Root-Cause Card

## Metadata

- ID: `nibiru-2022-08-03-nibiru-storage-8c6e9717`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-margin-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `post-state solvency validation`

## Violated Invariant

- Invariant: Leveraged position updates must be rejected if the resulting position would be below maintenance margin or create bad debt after all price, funding, and margin effects are applied.

## Trust Boundary

- Boundary: User-submitted derivatives trading message crosses into privileged margin accounting and vault solvency state.

## Attack Surface

- Entrypoint type: state-changing trading transaction / keeper message handler
- Sensitive sink: position update and vault accounting that can admit undercollateralized exposure

## Impact Pattern

- Primary impact: economic bad debt and solvency drift
- Secondary impact: market unfairness or forced socialized losses

## Short Reusable Lesson

- A leveraged trading flow failed to consistently validate the final position state after updates. The reusable shape is a state transition that mutates margin exposure before enforcing maintenance-margin and bad-debt invariants.
