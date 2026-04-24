# Root-Cause Card

## Metadata

- ID: `reth-2025-04-19-reth-core-logic-6ef19f403`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-upper-bound-check`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `numeric-bound-validation`

## Violated Invariant

- Invariant: If this function is part of the effective consensus-validation path, a block header should not be treated as valid when its `gas_limit` exceeds `MAXIMUM_GAS_LIMIT_BLOCK`. The patch enforces that invariant in `validate_header_gas`, but the supplied evidence does not establish whether this was previously exploitable or already enforced elsewhere.

## Trust Boundary

- Boundary: execution/engine state transition -> persistent storage

## Attack Surface

- Entrypoint type: state-storage-update-path
- Sensitive sink: canonical database, trie updates, or state provider output

## Impact Pattern

- Primary impact: consensus-integrity
- Secondary impact: state-integrity

## Short Reusable Lesson

- If this function is part of the effective consensus-validation path, a block header should not be treated as valid when its `gas_limit` exceeds `MAXIMUM_GAS_LIMIT_BLOCK`. The patch enforces that invariant in `validate_header_gas`, but the supplied evidence does not establish whether this was previously exploitable or already enforced elsewhere.
