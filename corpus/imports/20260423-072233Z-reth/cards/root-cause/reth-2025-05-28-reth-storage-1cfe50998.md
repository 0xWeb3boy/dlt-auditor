# Root-Cause Card

## Metadata

- ID: `reth-2025-05-28-reth-storage-1cfe50998`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `state-integrity-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `canonical-persistence-derived-state-completeness`

## Violated Invariant

- Invariant: Canonical persistence must not assume derived trie updates exist for forked ancestry; missing derived state must be detected, recomputed, or handled as a fallible condition.

## Trust Boundary

- Boundary: Forked in-memory block ancestry crossing into canonical persistence and database handoff.

## Attack Surface

- Entrypoint type: engine-tree-persistence
- Sensitive sink: Canonical block persistence and trie-update handoff.

## Impact Pattern

- Primary impact: Canonical persistence no longer silently assumes forked ancestry has complete trie updates.
- Secondary impact: Missing derived state becomes explicit and recoverable instead of implicit state-machine drift.

## Short Reusable Lesson

- The persistence path assumed trie updates were present when forked ancestry became canonical. The patch adds ancestor missing-data detection, makes persistence batching fallible, and guards trie-update extraction during canonical removal.
