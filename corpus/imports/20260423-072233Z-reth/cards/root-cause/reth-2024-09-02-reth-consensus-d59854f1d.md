# Root-Cause Card

## Metadata

- ID: `reth-2024-09-02-reth-consensus-d59854f1d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-runtime-bound-check`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: TODO

## Trust Boundary

- Boundary: TODO

## Attack Surface

- Entrypoint type: TODO
- Sensitive sink: TODO

## Impact Pattern

- Primary impact: TODO
- Secondary impact: TODO

## Short Reusable Lesson

- The evidence supports a runtime hardening/correctness fix in the engine tree pruning path. Before the patch, `remove_until` only asserted in debug builds that `finalized_num <= upper_bound`; after the patch, it clamps the value with `min(upper_bound)` and documents that behavior. The supplied snippets do not establish a concrete vulnerability, attacker control, or a demonstrated security impact.
