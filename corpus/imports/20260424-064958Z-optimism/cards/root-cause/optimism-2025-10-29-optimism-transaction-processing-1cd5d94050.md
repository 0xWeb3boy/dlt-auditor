# Root-Cause Card

## Metadata

- ID: `optimism-2025-10-29-optimism-transaction-processing-1cd5d94050`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: Optimism header validation must enforce fork-specific blob gas rules exactly: after Ecotone both blob_gas_used and excess_blob_gas must be present, excess_blob_gas must be zero on OP-stack blocks, and blob_gas_used is zero before Jovian but may carry current DA footprint after Jovian.

## Trust Boundary

- Boundary: sequencer/batch/transaction input -> derivation or execution engine

## Attack Surface

- Entrypoint type: transaction-handler or batch-derivation path
- Sensitive sink: block payload acceptance, execution attributes, or derived state transition

## Impact Pattern

- Primary impact: correctness-or-hardening
- Secondary impact: consensus-integrity

## Short Reusable Lesson

- Optimism header validation must enforce fork-specific blob gas rules exactly: after Ecotone both blob_gas_used and excess_blob_gas must be present, excess_blob_gas must be zero on OP-stack blocks, and blob_gas_used is zero before Jovian but may carry current DA footprint after Jovian. Similar bugs appear when transaction-handler or batch-derivation path code treats partially checked input as authoritative and lets it reach block payload acceptance, execution attributes, or derived state transition. The reusable fix is to enforce input-validation at the boundary and fail closed before state, privilege, or consensus-visible output changes.
