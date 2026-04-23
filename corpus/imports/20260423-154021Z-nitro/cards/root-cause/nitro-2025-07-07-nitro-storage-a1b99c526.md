# Root-Cause Card

## Metadata

- ID: `nitro-2025-07-07-nitro-storage-a1b99c526`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `verification-state-retention`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `finalized-verification-state-retention`

## Violated Invariant

- Invariant: Validation backlog and delayed-message tracking state should be explicitly initialized and retained until finalized cleanup conditions are met.

## Trust Boundary

- Boundary: `persisted delayed-message metadata->validation backlog and cleanup logic`

## Attack Surface

- Entrypoint type: `state-retention-or-cleanup`
- Sensitive sink: `discarding, retaining, or validating pending message state`

## Impact Pattern

- Primary impact: `state-integrity`
- Secondary impact: `none`

## Short Reusable Lesson

- Validation backlog and delayed-message tracking state should be explicitly initialized and retained until finalized cleanup conditions are met. The patch is well supported as a correctness/state-handling change in MEL delayed-message tracking. It replaces the older seen-unread deque flow with an explicitly initialized delayedMetaBacklog, stops silently creating missing tracking state during accumulation, and changes trimming logic to depend on finalized MEL state. The robust fix is to make the privileged sink consume authoritative state or policy context that has already been validated, and fail closed when that binding is missing.
