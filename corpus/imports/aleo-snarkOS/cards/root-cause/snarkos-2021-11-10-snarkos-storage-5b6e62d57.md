# Root-Cause Card

## Metadata

- ID: `snarkos-2021-11-10-snarkos-storage-5b6e62d57`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-fork-choice`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `fork-choice-weight-validation`

## Violated Invariant

- Invariant: Fork switching must compare canonical chain weight or accumulated work from the common ancestor, not raw height alone.

## Trust Boundary

- Boundary: `peer-chain->local-ledger-sync`

## Attack Surface

- Entrypoint type: `state-transition`
- Sensitive sink: ledger rollback and canonical fork selection
- Attacker capability: serve an alternate chain during sync; control peer-reported height/blocks.
- Preconditions: node may switch forks based on sync comparison; alternate fork shares a common ancestor.

## Impact Pattern

- Primary impact: incorrect reorg choice.
- Secondary impact: sync to weaker or invalid economic fork.
- Severity guide: `high` for `consensus-integrity` when the affected path is reachable from untrusted peers or RPC callers.

## Short Reusable Lesson

- Fork switching must compare canonical chain weight or accumulated work from the common ancestor, not raw height alone. The reusable lesson is to enforce the property at the boundary where untrusted data first becomes trusted state, and to keep the fix narrow enough that compensating controls remain visible during review.

## Evidence Anchor

- Raw finding summary: The patch changes snarkOS network ledger synchronization from a height-based fork switch rule to a weight-based rule. The evidence supports a consensus-relevant fork-choice fix, but does not establish a concrete exploit path or broader impact beyond incorrect reorg behavior. 1. In `src/network/ledger.rs`, the patch replaces `// and the peer has a higher block height, proceed to switch to the fork.` with `// and the peer has a heavier chain, proceed to switch to the fork.`. 2. In `src/network/ledger.rs`, the patch replaces `info!("Found a longer fork, rolling ledger back to block {}", maximum_common_ancestor);` with `info!("Found a heavier fork, rolling ledger back to block {}", maximum_commo
