# Root-Cause Card

## Metadata

- ID: `stacks-core-2024-03-12-stacks-core-storage-481b01c536`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `cross-cycle-stale-state`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `fresh-state-lifecycle-binding`

## Violated Invariant

- Invariant: Consensus and validation decisions must use state from the current fork, reward cycle, and lifecycle epoch, not cached or prior-cycle data.

## Trust Boundary

- Boundary: Persisted or peer-derived chain state crosses into storage-backed validation.

## Attack Surface

- Entrypoint type: `state_database_lookup_or_update`
- Sensitive sink: canonical state database, cached validation state, or durable index

## Impact Pattern

- Primary impact: state-integrity
- Secondary impact: stale-state-use

## Short Reusable Lesson

- The patch likely fixes a security-relevant stale-state issue in the signer database. It changes block storage, lookup, and removal from being keyed only by signer_signature_hash to being scoped by reward_cycle plus signer_signature_hash. The commit message explicitly says this prevents signers from acting on blocks from the previous cycle. The evidence supports a cross-cycle stale-state fix, but not a stronger claim about exploitability, fund loss, or consensus failure.
