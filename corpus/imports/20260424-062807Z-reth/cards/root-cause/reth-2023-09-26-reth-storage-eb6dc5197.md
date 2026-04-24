# Root-Cause Card

## Metadata

- ID: `reth-2023-09-26-reth-storage-eb6dc5197`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-rule-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `protocol-rule-enforcement`

## Violated Invariant

- Invariant: New-payload validation should enforce fork-gated consensus rules before a payload is treated as well formed. In the supplied evidence, that specifically means rejecting blob transactions when Cancun is not active for the block timestamp.

## Trust Boundary

- Boundary: execution/engine state transition -> persistent storage

## Attack Surface

- Entrypoint type: state-storage-update-path
- Sensitive sink: canonical database, trie updates, or state provider output

## Impact Pattern

- Primary impact: consensus-integrity
- Secondary impact: protocol-input-validation

## Short Reusable Lesson

- New-payload validation should enforce fork-gated consensus rules before a payload is treated as well formed. In the supplied evidence, that specifically means rejecting blob transactions when Cancun is not active for the block timestamp.
