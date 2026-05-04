# Root-Cause Card

## Metadata

- ID: `fuel-core-2026-04-23-fuel-core-storage-bf285299c4`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `leader-lease-release-delay`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `lifecycle-cleanup`

## Violated Invariant

- Only logical owners of a leader lease should keep release guards alive; short-lived worker clones must not delay failover cleanup.

## Trust Boundary

- Boundary: `async-worker-clone->leader-lease-lifecycle`
- Entrypoint type: `state-transition`
- Sensitive sink: `Redis leader lease release and failover availability`

## Attack Surface

- Cause or coincide with slow backend publish tasks during leader shutdown or failover.
- Benefit from lease release being delayed by task-only clones.

## Exploit Preconditions

- Task-spawned adapter clones inherit the same Arc-backed release guard as logical owners.
- Drop uses strong_count to decide whether to release the lease.

## Impact Pattern

- Primary impact: `denial-of-service`
- Secondary impact: `consensus-liveness`
- Blast radius: `chain-wide`
- Severity guess: `medium`

## Short Reusable Lesson

- Lifecycle guards encode ownership; do not blindly clone them into async workers that should not affect cleanup decisions.
