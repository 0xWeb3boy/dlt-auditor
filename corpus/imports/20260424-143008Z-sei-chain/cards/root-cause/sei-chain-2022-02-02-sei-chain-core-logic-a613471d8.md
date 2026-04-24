# Root-Cause Card

## Metadata

- ID: `sei-chain-2022-02-02-sei-chain-core-logic-a613471d8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-determinism`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `deterministic-consensus-serialization`

## Violated Invariant

- Invariant: Bytes committed into consensus results must be deterministic for the same logical outcome across all node builds and environments.

## Trust Boundary

- Boundary: module error path -> consensus-visible acknowledgement/result bytes

## Attack Surface

- Entrypoint type: packet-or-transaction-error-handler
- Sensitive sink: serializing acknowledgement or transaction result bytes into committed state

## Impact Pattern

- Primary impact: consensus-divergence
- Secondary impact: state-consistency

## Short Reusable Lesson

- Replace raw error-string acknowledgement serialization in consensus state with a module-level deterministic acknowledgement constructor backed by stable acknowledgement text and deterministic error metadata where applicable. IBC acknowledgements are consensus-state data. Consensus nodes must commit identical acknowledgement bytes for the same packet result.
