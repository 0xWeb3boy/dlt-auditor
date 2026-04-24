# Root-Cause Card

## Metadata

- ID: `sei-chain-2026-02-09-sei-chain-transaction-processing-d9f1de1a4`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `app-hash-state-accounting-inconsistency`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `alternate-execution-accounting-parity`

## Violated Invariant

- Invariant: Alternate execution engines must propagate the same finalized deltas and state visibility as the canonical block execution path.

## Trust Boundary

- Boundary: giga/alternate EVM execution -> canonical bank/endblock consensus state

## Attack Surface

- Entrypoint type: block-execution-finalization
- Sensitive sink: committing surplus, deferred metadata, and store writes used for app hash

## Impact Pattern

- Primary impact: liveness
- Secondary impact: state-accounting

## Short Reusable Lesson

- Align an alternate execution path with canonical consensus accounting by preserving finalized deltas, propagating them to deferred metadata, and flushing alternate store layers before downstream state reads. App-hash computation depends on deterministic state and metadata before EndBlock. Discarding finalized surplus can lose consensus-relevant accounting information.
