# Root-Cause Card

## Metadata

- ID: `sui-2026-02-27-sui-transaction-processing-48d0a9bce8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `malformed-transaction-panic`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: Malformed or adversarial inputs must be rejected before they reach parsing, execution, or state-commit logic that assumes well-formed data.

## Trust Boundary

- Boundary: submitted transaction or validator response -> execution/effects pipeline

## Attack Surface

- Entrypoint type: transaction-handler
- Sensitive sink: committing security-sensitive protocol state

## Impact Pattern

- Primary impact: availability
- Secondary impact: context-dependent

## Short Reusable Lesson

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. Consolidate tx checking in signing and simulate (#25624) appears to strengthen state integrity in the transaction-processing path of sui. The strongest evidence spans `crates/sui-core/src/authority.rs` and `crates/sui-core/src/authority.rs`.
