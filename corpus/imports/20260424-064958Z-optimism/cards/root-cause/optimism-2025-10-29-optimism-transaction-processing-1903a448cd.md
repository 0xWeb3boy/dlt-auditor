# Root-Cause Card

## Metadata

- ID: `optimism-2025-10-29-optimism-transaction-processing-1903a448cd`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-rule-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `integrity-binding`

## Violated Invariant

- Invariant: Header validation must enforce the OP-stack fork-specific blob-gas rules: after Ecotone, both blob_gas_used and excess_blob_gas must be present; excess_blob_gas must be 0; before Jovian, blob_gas_used must also be 0; after Jovian, blob_gas_used is allowed to represent the current DA footprint instead of following generic EIP-4844 parent-derived coupling.

## Trust Boundary

- Boundary: external proof/data provider -> verifier/derivation code

## Attack Surface

- Entrypoint type: proof-or-data-verification path
- Sensitive sink: acceptance of cryptographic, blob, preimage, or proof data into derivation/state

## Impact Pattern

- Primary impact: consensus-divergence-risk
- Secondary impact: consensus-integrity

## Short Reusable Lesson

- Header validation must enforce the OP-stack fork-specific blob-gas rules: after Ecotone, both blob_gas_used and excess_blob_gas must be present; excess_blob_gas must be 0; before Jovian, blob_gas_used must also be 0; after Jovian, blob_gas_used is allowed to represent the current DA footprint instead of following generic EIP-4844 parent-derived coupling. Similar bugs appear when proof-or-data-verification path code treats partially checked input as authoritative and lets it reach acceptance of cryptographic, blob, preimage, or proof data into derivation/state. The reusable fix is to enforce integrity-binding at the boundary and fail closed.
