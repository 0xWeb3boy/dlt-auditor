# Root-Cause Card

## Metadata

- ID: `reth-2023-05-04-reth-consensus-010b600f3`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-consensus-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `protocol-rule-enforcement`

## Violated Invariant

- Invariant: A block admitted into the blockchain tree should reference its parent consistently: if `parent_hash` resolves to a canonical block, that block's canonical height should agree with the advertised `parent.number`.

## Trust Boundary

- Boundary: consensus layer signal -> execution client forkchoice/block state

## Attack Surface

- Entrypoint type: engine-api/forkchoice-handler
- Sensitive sink: canonical head, payload status, or pipeline scheduling

## Impact Pattern

- Primary impact: consensus-integrity-risk
- Secondary impact: consensus-integrity

## Short Reusable Lesson

- A block admitted into the blockchain tree should reference its parent consistently: if `parent_hash` resolves to a canonical block, that block's canonical height should agree with the advertised `parent.number`.
