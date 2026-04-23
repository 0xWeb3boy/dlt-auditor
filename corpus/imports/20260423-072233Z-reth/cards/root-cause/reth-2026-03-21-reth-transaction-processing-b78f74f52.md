# Root-Cause Card

## Metadata

- ID: `reth-2026-03-21-reth-transaction-processing-b78f74f52`
- Bug family: `authz_and_role_gates`
- Bug class: `validation-bypass`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `narrow-validator-exception-scoping`

## Violated Invariant

- Invariant: Special-case block formats may relax only the specific fields that are non-comparable; they must not bypass core payload identity or state-root integrity checks.

## Trust Boundary

- Boundary: Synthetic or segmented payload metadata crossing into the production payload validator and engine-tree post-execution checks.

## Attack Surface

- Entrypoint type: engine-payload-validation
- Sensitive sink: Payload acceptance and post-execution state validation.

## Impact Pattern

- Primary impact: Core payload integrity checks remain enforced on special-case payloads.
- Secondary impact: Reduces risk that tooling accommodations leak into production validation.

## Short Reusable Lesson

- Broad validator exceptions for special payload forms allowed hash or state-root checks to be skipped. The patch removes zero-hash sentinel behavior, always compares the executed state root to the header, and narrows env-switch handling to receipt-derived fields only.
