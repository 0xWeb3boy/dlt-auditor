# Root-Cause Card

## Metadata

- ID: `bor-2019-03-12-bor-transaction-processing-7504dbd6e`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `resource-accounting-overflow`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `arithmetic bounds and resource accounting`

## Violated Invariant

- Invariant: Attacker-controlled input must be bounded and rejected before it can drive unbounded allocation, expensive processing, queue growth, or process termination.

## Trust Boundary

- Boundary: untrusted block, header, transaction, or state data to consensus engine boundary

## Attack Surface

- Entrypoint type: block/header/transaction validation or state-transition path
- Sensitive sink: canonical chain selection, state root commitment, or consensus state mutation

## Impact Pattern

- Primary impact: resource-accounting-integrity
- Secondary impact: medium severity conditions

## Short Reusable Lesson

- Arithmetic around memory sizing and gas charging was refactored to an explicit checked uint64 path, suggesting prior correctness risk at that boundary; however, the supplied hunks do not prove that the earlier code was actually vulnerable in a security sense.
