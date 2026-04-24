# Root-Cause Card

## Metadata

- ID: `sui-2023-04-08-sui-storage-e0c1591d99`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `rpc-object-digest-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: Malformed or adversarial inputs must be rejected before they reach parsing, execution, or state-commit logic that assumes well-formed data.

## Trust Boundary

- Boundary: executed effects or checkpoint data -> authenticated persistent state

## Attack Surface

- Entrypoint type: state-transition-storage-update
- Sensitive sink: persisting or serving authenticated ledger state

## Impact Pattern

- Primary impact: rpc-reporting-integrity
- Secondary impact: client-view-divergence

## Short Reusable Lesson

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. The patch hardens Sui JSON-RPC `balanceChanges` construction by carrying object digests into the coin-fetching path and asserting that locally fetched coin objects match those digests before their contents are used. The evidence supports an RPC reporting integrity fix for stale or inconsistent local object reads.
