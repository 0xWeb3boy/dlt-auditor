# Root-Cause Card

## Metadata

- ID: `avalanchego-2023-09-27-avalanchego-transaction-processing-8e6f2f83e6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `hardening-or-correctness-fix`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `required-context-presence`

## Violated Invariant

- Invariant: A verifier that requires external execution context must fail closed when that context is absent or incomplete.

## Trust Boundary

- Boundary: Transaction predicate data crosses from block execution context into predicate verification.

## Attack Surface

- Entrypoint type: predicate validation during transaction or block processing
- Sensitive sink: predicate verification result used to admit transaction execution

## Impact Pattern

- Primary impact: validation-hardening, consensus-correctness
- Secondary impact: medium_high_integrity

## Root Cause

- `CheckPredicates` lacked an explicit validation step ensuring that required predicate context was present before predicate verification work continued. ## Walkthrough 1. `CheckPredicates` validates intrinsic gas for the transaction. 2. It initializes predicate results and returns early when no predicates are configured. 3. It derives predicate arguments from the transaction access list. 4.

## Short Reusable Lesson

- Predicate checking gained explicit missing-context errors before verification-sensitive logic continues. The reusable shape is a validation function that accepts optional context but must require it whenever the checked object depends on it.
