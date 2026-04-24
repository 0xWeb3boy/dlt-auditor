# Root-Cause Card

## Metadata

- ID: `reth-2024-04-16-reth-storage-33b195af3`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `fork-hash-reconstruction`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `fork-state-consistency`

## Violated Invariant

- Invariant: When reconstructing a non-canonical branch's block-hash view, ancestor traversal should not replace an already selected hash for the same block number or extend the view past the original branch tip.

## Trust Boundary

- Boundary: forkchoice or sidechain state -> persistent storage provider

## Attack Surface

- Entrypoint type: blockchain-tree/state-provider-path
- Sensitive sink: canonical state view, fork ancestry, or persisted trie updates

## Impact Pattern

- Primary impact: consensus-integrity-risk
- Secondary impact: state-integrity

## Short Reusable Lesson

- When reconstructing a non-canonical branch's block-hash view, ancestor traversal should not replace an already selected hash for the same block number or extend the view past the original branch tip.
