# Root-Cause Card

## Metadata

- ID: `reth-2025-10-29-reth-transaction-processing-77ef028ac`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `cryptographic-data-binding`

## Violated Invariant

- Invariant: For OP Stack headers, blob-gas fields must follow fork-specific rules: after Ecotone the fields must be present, `excess_blob_gas` must be `0`, and `blob_gas_used` is `0` before Jovian but has Jovian-specific semantics after that fork.

## Trust Boundary

- Boundary: blob transaction and sidecar -> transaction validator

## Attack Surface

- Entrypoint type: blob-transaction-validator
- Sensitive sink: blob transaction acceptance and propagation

## Impact Pattern

- Primary impact: consensus-integrity
- Secondary impact: none proven

## Short Reusable Lesson

- For OP Stack headers, blob-gas fields must follow fork-specific rules: after Ecotone the fields must be present, `excess_blob_gas` must be `0`, and `blob_gas_used` is `0` before Jovian but has Jovian-specific semantics after that fork.
