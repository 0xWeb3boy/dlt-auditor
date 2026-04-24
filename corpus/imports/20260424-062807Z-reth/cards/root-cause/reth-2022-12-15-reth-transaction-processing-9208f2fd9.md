# Root-Cause Card

## Metadata

- ID: `reth-2022-12-15-reth-transaction-processing-9208f2fd9`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `fork-selection-logic`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `fork-state-consistency`

## Violated Invariant

- Invariant: Block execution should use the REVM spec active for the block number being executed, and receipt status should only encode explicit success or explicit revert outcomes. The provided evidence shows this invariant was corrected, but does not by itself establish a security exploit or real-world vulnerability.

## Trust Boundary

- Boundary: block or transaction input -> execution-layer validator

## Attack Surface

- Entrypoint type: transaction/block-validation-path
- Sensitive sink: transaction acceptance or consensus rule application

## Impact Pattern

- Primary impact: consensus-integrity
- Secondary impact: none proven

## Short Reusable Lesson

- Block execution should use the REVM spec active for the block number being executed, and receipt status should only encode explicit success or explicit revert outcomes. The provided evidence shows this invariant was corrected, but does not by itself establish a security exploit or real-world vulnerability.
