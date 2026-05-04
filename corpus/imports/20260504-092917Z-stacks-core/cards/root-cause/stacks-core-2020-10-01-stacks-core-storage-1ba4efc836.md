# Root-Cause Card

## Metadata

- ID: `stacks-core-2020-10-01-stacks-core-storage-1ba4efc836`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `delegated-stacking-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `canonical-input-validation`

## Violated Invariant

- Invariant: Protocol inputs must be normalized and validated in their canonical context before they influence state, signatures, or consensus outcomes.

## Trust Boundary

- Boundary: Persisted or peer-derived chain state crosses into storage-backed validation.

## Attack Surface

- Entrypoint type: `state_database_lookup_or_update`
- Sensitive sink: canonical state database, cached validation state, or durable index

## Impact Pattern

- Primary impact: economic-integrity
- Secondary impact: consensus-validation

## Short Reusable Lesson

- The patch adjusts PoX delegated stacking behavior: the VM special handler no longer requires the returned stacker to equal the transaction sender, and the delegated stacking path adds a balance check against `stacker`. This is plausibly security relevant, but the evidence more directly supports a delegation semantics and validation correctness fix than a confirmed vulnerability fix.
