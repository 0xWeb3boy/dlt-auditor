# Root-Cause Card

## Metadata

- ID: `reth-2023-09-26-reth-storage-eb6dc5197`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-rule-validation`
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

- The patch adds an explicit pre-Cancun no-blob check in the beacon engine's payload-validation path and routes that case through a distinct `BeaconOnNewPayloadError`. The evidence supports that a fork-specific validation step was missing in this path, but it does not by itself prove prior acceptance into canonical state, exploitability, or a realized consensus failure.
