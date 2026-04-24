# Root-Cause Card

## Metadata

- ID: `reth-2024-04-25-reth-rpc-client-api-33e7e0208`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-bad-peer-penalization`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `peer-policy-gating`

## Violated Invariant

- Invariant: The fetch scheduler should prefer the best eligible peer and should not immediately reuse a peer whose most recent response was likely bad, such as an empty block-bodies response.

## Trust Boundary

- Boundary: remote peer response -> fetch scheduler

## Attack Surface

- Entrypoint type: peer-response-handler
- Sensitive sink: peer selection and retry scheduling

## Impact Pattern

- Primary impact: abuse-resistance
- Secondary impact: consensus-integrity

## Short Reusable Lesson

- The fetch scheduler should prefer the best eligible peer and should not immediately reuse a peer whose most recent response was likely bad, such as an empty block-bodies response.
