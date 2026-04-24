# Root-Cause Card

## Metadata

- ID: `sei-chain-2026-02-12-sei-chain-rpc-client-api-f45028f01`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-state-mismatch`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `certified-proposal-state-binding`

## Violated Invariant

- Invariant: Commit-step block reconstruction must be bound to the block ID and part-set header certified by the commit evidence.

## Trust Boundary

- Boundary: peer proposal/block parts -> local commit-step consensus state

## Attack Surface

- Entrypoint type: consensus-commit-handler
- Sensitive sink: reconstructing or accepting ProposalBlock for commit processing

## Impact Pattern

- Primary impact: consensus-liveness
- Secondary impact: node-halt

## Short Reusable Lesson

- Anchor commit-step proposal handling and block reconstruction to the certified commit BlockID, ignore conflicting proposals, avoid rebuilding over existing proposal block state, and fetch block parts for the certified PartSetHeader. Addresses a consensus halt/liveness failure mode named by the commit subject.
