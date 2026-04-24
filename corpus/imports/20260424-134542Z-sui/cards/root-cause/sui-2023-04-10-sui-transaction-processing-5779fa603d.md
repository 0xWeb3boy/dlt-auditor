# Root-Cause Card

## Metadata

- ID: `sui-2023-04-10-sui-transaction-processing-5779fa603d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `monetary-accounting-invariant-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `resource-accounting`

## Violated Invariant

- Invariant: Every state transition that consumes resources or changes balances must update the corresponding accounting state exactly once and within protocol bounds.

## Trust Boundary

- Boundary: submitted transaction or validator response -> execution/effects pipeline

## Attack Surface

- Entrypoint type: transaction-handler
- Sensitive sink: committing fees, balances, or resource accounting state

## Impact Pattern

- Primary impact: asset-integrity
- Secondary impact: context-dependent

## Short Reusable Lesson

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. The patch adds configuration plumbing for an expensive deep per-transaction SUI conservation check in Sui transaction execution.
