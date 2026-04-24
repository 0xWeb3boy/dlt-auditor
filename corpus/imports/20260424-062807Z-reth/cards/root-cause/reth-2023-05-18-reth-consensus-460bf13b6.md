# Root-Cause Card

## Metadata

- ID: `reth-2023-05-18-reth-consensus-460bf13b6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `protocol-rule-enforcement`

## Violated Invariant

- Invariant: Consensus-facing forkchoice and payload validation should determine whether a referenced block is canonical using the node's full canonical view, including persisted DB state when in-memory indices are incomplete, so protocol responses do not weaken an invalid condition into a syncing/unknown classification.

## Trust Boundary

- Boundary: consensus layer signal -> execution client forkchoice/block state

## Attack Surface

- Entrypoint type: engine-api/forkchoice-handler
- Sensitive sink: canonical head, payload status, or pipeline scheduling

## Impact Pattern

- Primary impact: consensus-integrity
- Secondary impact: none proven

## Short Reusable Lesson

- Consensus-facing forkchoice and payload validation should determine whether a referenced block is canonical using the node's full canonical view, including persisted DB state when in-memory indices are incomplete, so protocol responses do not weaken an invalid condition into a syncing/unknown classification.
