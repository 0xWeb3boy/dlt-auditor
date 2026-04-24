# Root-Cause Card

## Metadata

- ID: `reth-2023-06-06-reth-storage-c0fb169da`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-error-handling`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `protocol-rule-enforcement`

## Violated Invariant

- Invariant: Consensus-related failures should be represented as validation failures with enough block context for the pipeline to reject or recover consistently.

## Trust Boundary

- Boundary: execution/engine state transition -> persistent storage

## Attack Surface

- Entrypoint type: state-storage-update-path
- Sensitive sink: canonical database, trie updates, or state provider output

## Impact Pattern

- Primary impact: consensus-integrity-risk
- Secondary impact: consensus-integrity

## Short Reusable Lesson

- Consensus-related failures should be represented as validation failures with enough block context for the pipeline to reject or recover consistently.
