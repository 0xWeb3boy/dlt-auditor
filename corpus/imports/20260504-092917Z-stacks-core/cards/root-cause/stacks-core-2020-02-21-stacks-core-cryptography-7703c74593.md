# Root-Cause Card

## Metadata

- ID: `stacks-core-2020-02-21-stacks-core-cryptography-7703c74593`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-resource-accounting`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `resource-bounds-and-error-containment`

## Violated Invariant

- Invariant: Untrusted inputs and execution paths must be bounded and must fail closed without panics, unmetered work, or inconsistent accounting.

## Trust Boundary

- Boundary: Persisted or peer-derived chain state crosses into storage-backed validation.

## Attack Surface

- Entrypoint type: `state_database_lookup_or_update`
- Sensitive sink: canonical state database, cached validation state, or durable index

## Impact Pattern

- Primary impact: resource-exhaustion-risk
- Secondary impact: denial-of-service

## Short Reusable Lesson

- The patch adds cost-accounting propagation to trait signature parsing. Before the change, `parse_trait_type_repr` called `TypeSignature::parse_type_repr` for trait function argument and return types without passing a `CostTracker`. After the change, `parse_trait_type_repr` accepts a mutable tracker, the define-trait runtime path passes the VM `Environment`, and recursive type parsing can charge its existing `TYPE_PARSE_STEP` cost.
