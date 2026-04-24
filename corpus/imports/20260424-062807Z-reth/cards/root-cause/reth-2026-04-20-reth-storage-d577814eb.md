# Root-Cause Card

## Metadata

- ID: `reth-2026-04-20-reth-storage-d577814eb`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `protocol-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `protocol-rule-enforcement`

## Violated Invariant

- Invariant: Engine API validation must decide whether Amsterdam-era fields are allowed or required using the active fork timestamp, the exact engine method version, and the message kind, rather than a coarse version cutoff alone.

## Trust Boundary

- Boundary: execution/engine state transition -> persistent storage

## Attack Surface

- Entrypoint type: state-storage-update-path
- Sensitive sink: canonical database, trie updates, or state provider output

## Impact Pattern

- Primary impact: protocol-integrity
- Secondary impact: state-integrity

## Short Reusable Lesson

- Engine API validation must decide whether Amsterdam-era fields are allowed or required using the active fork timestamp, the exact engine method version, and the message kind, rather than a coarse version cutoff alone.
