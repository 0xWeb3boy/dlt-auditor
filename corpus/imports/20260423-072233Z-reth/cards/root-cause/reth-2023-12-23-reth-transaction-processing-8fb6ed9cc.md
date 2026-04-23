# Root-Cause Card

## Metadata

- ID: `reth-2023-12-23-reth-transaction-processing-8fb6ed9cc`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incorrect-fork-gating`
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

- The patch corrects the hardfork check used in the `Transaction::Eip1559` validation path, changing it from `Berlin` to `London` in a consensus validation function. The evidence supports a protocol-rule mismatch in transaction validation, but it does not establish a concrete security impact beyond incorrect gating.
