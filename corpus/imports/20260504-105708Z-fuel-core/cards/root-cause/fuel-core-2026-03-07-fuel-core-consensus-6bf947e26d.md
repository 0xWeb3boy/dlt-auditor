# Root-Cause Card

## Metadata

- ID: `fuel-core-2026-03-07-fuel-core-consensus-6bf947e26d`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `consensus-safety`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `error-propagation`

## Violated Invariant

- Failures reading authoritative consensus progress must remain distinguishable from an empty or clean state.

## Trust Boundary

- Boundary: `durable-consensus-store->leader-reconciliation`
- Entrypoint type: `state-transition`
- Sensitive sink: `leader reconciliation and next-block production decision`

## Attack Surface

- Cause or coincide with Redis connection, timeout, or script-read failures during leader handoff.
- Benefit from a node treating unknown committed state as absent.

## Exploit Preconditions

- Consensus progress is reconstructed from external Redis streams.
- Read failures are converted to empty vectors instead of errors.

## Impact Pattern

- Primary impact: `consensus-integrity`
- Secondary impact: `fork-risk`
- Blast radius: `chain-wide`
- Severity guess: `high`

## Short Reusable Lesson

- Consensus recovery must fail closed on unknown durable state; empty and unreadable are different security states.
