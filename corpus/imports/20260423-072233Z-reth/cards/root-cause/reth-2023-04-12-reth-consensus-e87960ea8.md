# Root-Cause Card

## Metadata

- ID: `reth-2023-04-12-reth-consensus-e87960ea8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `forkchoice-input-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: TODO

## Trust Boundary

- Boundary: TODO

## Attack Surface

- Entrypoint type: TODO
- Sensitive sink: TODO

## Impact Pattern

- Primary impact: TODO
- Secondary impact: TODO

## Short Reusable Lesson

- The patch is well supported as a beacon-engine forkchoice/pipeline state-machine fix, but the provided evidence does not establish a concrete vulnerability. It moves the pipeline-run decision earlier and bases it on the full `ForkchoiceState`, including whether the announced head exists locally, rather than relying on a later fallback in payload processing.
