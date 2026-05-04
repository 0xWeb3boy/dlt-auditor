# Root-Cause Card

## Metadata

- ID: `stacks-core-2019-08-29-stacks-core-cryptography-6b6cbd3f36`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-constructor-validation`
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

- Primary impact: resource-exhaustion
- Secondary impact: protocol-integrity

## Short Reusable Lesson

- The patch changes Clarity VM list type/value construction to rely on constructor-validated ListTypeData/TypeSignature metadata instead of direct field construction and repeated downstream size checks. This supports an invariant-cleanup or hardening interpretation around MAX_VALUE_SIZE, but the supplied evidence does not establish an externally reachable vulnerability or concrete security impact.
