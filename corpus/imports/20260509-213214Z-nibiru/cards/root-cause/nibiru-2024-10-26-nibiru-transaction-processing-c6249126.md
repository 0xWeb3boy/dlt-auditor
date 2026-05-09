# Root-Cause Card

## Metadata

- ID: `nibiru-2024-10-26-nibiru-transaction-processing-c6249126`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `precompile-rollback-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `atomic rollback of cross-runtime side effects`

## Violated Invariant

- Invariant: All native side effects produced during a precompile call must share the same transaction journal and rollback boundary as the EVM call that triggered them.

## Trust Boundary

- Boundary: EVM precompile execution crosses into SDK multistore and module account state.

## Attack Surface

- Entrypoint type: state-changing EVM precompile call
- Sensitive sink: SDK multistore cache snapshots, StateDB journal, and commit path

## Impact Pattern

- Primary impact: cross-runtime state inconsistency
- Secondary impact: failed calls leaving native side effects

## Short Reusable Lesson

- Precompile multistore snapshots were moved into the main transaction journal and tied to the EVM transaction context to preserve atomic rollback semantics.
