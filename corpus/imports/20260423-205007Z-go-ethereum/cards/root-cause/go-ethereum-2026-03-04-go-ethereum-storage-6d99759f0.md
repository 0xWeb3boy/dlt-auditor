# Root-Cause Card

## Metadata

- ID: `go-ethereum-2026-03-04-go-ethereum-storage-6d99759f0`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `rpc-persistent-state-side-effect`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `state-transition-consistency`

## Violated Invariant

- Invariant: Debug/RPC execution paths used for witness generation or inspection should not persist computed block/state data unless the caller explicitly requests normal chain-import side effects.

## Trust Boundary

- Boundary: Untrusted RPC or debug request parameters reaching privileged node logic.

## Attack Surface

- Entrypoint type: `rpc method`
- Sensitive sink: `persistent state writes or canonical-head side effects behind an RPC/debug path`

## Impact Pattern

- Primary impact: `state-integrity`
- Secondary impact: `resource-exhaustion`

## Short Reusable Lesson

- The patch separates read-only execution from persistent writes in go-ethereum's block execution path.
