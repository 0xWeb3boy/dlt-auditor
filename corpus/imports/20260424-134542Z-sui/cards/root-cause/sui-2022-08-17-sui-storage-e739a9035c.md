# Root-Cause Card

## Metadata

- ID: `sui-2022-08-17-sui-storage-e739a9035c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unbounded-retry-resource-control`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `resource-accounting`

## Violated Invariant

- Invariant: Untrusted work must be bounded, attributed, and charged or throttled before it can consume shared validator resources.

## Trust Boundary

- Boundary: executed effects or checkpoint data -> authenticated persistent state

## Attack Surface

- Entrypoint type: state-transition-storage-update
- Sensitive sink: consuming validator CPU, memory, network, or execution budget

## Impact Pattern

- Primary impact: availability
- Secondary impact: context-dependent

## Short Reusable Lesson

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. The patch allows online retry of interrupted transactions, but moves retry accounting into the WAL begin path and rejects retries above `MAX_TX_RECOVERY_RETRY`. The evidence supports security-relevant resource-control hardening against poison-pill or crash-loop style retries, but not a confirmed exploitable vulnerability.
