# Root-Cause Card

## Metadata

- ID: `reth-2026-04-21-reth-storage-d92ad5aa3`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-state-binding`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `state-coordinate-consistency`

## Violated Invariant

- Invariant: Overlay-backed state views should be resolved, reverted, and cached against the exact anchor block hash when fork identity matters; block height alone is not a sufficient identity.

## Trust Boundary

- Boundary: forkchoice or sidechain state -> persistent storage provider

## Attack Surface

- Entrypoint type: blockchain-tree/state-provider-path
- Sensitive sink: canonical state view, fork ancestry, or persisted trie updates

## Impact Pattern

- Primary impact: state-integrity
- Secondary impact: none proven

## Short Reusable Lesson

- Overlay-backed state views should be resolved, reverted, and cached against the exact anchor block hash when fork identity matters; block height alone is not a sufficient identity.
