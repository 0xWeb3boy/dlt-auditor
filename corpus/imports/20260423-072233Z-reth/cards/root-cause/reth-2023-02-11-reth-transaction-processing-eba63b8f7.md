# Root-Cause Card

## Metadata

- ID: `reth-2023-02-11-reth-transaction-processing-eba63b8f7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-transition-check`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `complete-hardfork-transition-predicate`

## Violated Invariant

- Invariant: Hardfork activation gates must include every transition-defining field needed to classify the current block side, not only accumulated chain state.

## Trust Boundary

- Boundary: External payloads, headers, and block bodies crossing into hardfork activation checks during sync, Engine API validation, and execution.

## Attack Surface

- Entrypoint type: consensus-transition-validation
- Sensitive sink: Paris/Merge activation decision, reward suppression, and zero-difficulty validation.

## Impact Pattern

- Primary impact: Boundary-era blocks are classified with the full transition condition.
- Secondary impact: Payload validation, execution rewards, and sync validation use consistent fork activation semantics.

## Short Reusable Lesson

- Paris activation checks used cumulative total difficulty without consistently passing current block or payload difficulty. The patch expands the predicate inputs across Engine API payload validation, reward logic, and total-difficulty stage validation.
