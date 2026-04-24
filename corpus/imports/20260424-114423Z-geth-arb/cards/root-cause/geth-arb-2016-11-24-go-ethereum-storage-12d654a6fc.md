# Root-Cause Card

## Metadata

- ID: `geth-arb-2016-11-24-go-ethereum-storage-12d654a6fc`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `consensus-state-divergence`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `state-transition-journal-consistency`

## Violated Invariant

- Invariant: State transitions must journal every account touch that affects consensus deletion, emptiness, or trie commitment so reverts and final roots are deterministic.

## Trust Boundary

- Boundary: transaction execution -> authenticated account state journal

## Attack Surface

- Entrypoint type: EVM state transition path
- Sensitive sink: state trie commitment and consensus state root

## Impact Pattern

- Primary impact: consensus-integrity
- Secondary impact: state-integrity
- Severity guide: high

## Short Reusable Lesson

- Zero-value account touches were not journaled consistently, so revert and deletion semantics could diverge around empty accounts. Record account touches explicitly in the journal and replay/revert them consistently before computing committed state.
