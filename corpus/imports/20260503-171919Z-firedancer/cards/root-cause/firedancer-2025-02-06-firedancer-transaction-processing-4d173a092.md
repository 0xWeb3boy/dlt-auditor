# Root-Cause Card

## Metadata

- ID: `firedancer-2025-02-06-firedancer-transaction-processing-4d173a092`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-accounting-mismatch`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `multi-dimension-resource-accounting`

## Violated Invariant

- Invariant: Consensus-critical schedulers must charge compute units and loaded-account-data costs in the same dimensions used for admission and execution limits.

## Trust Boundary

- Boundary: Transaction resource usage crossing into pack/bank admission accounting.

## Attack Surface

- Entrypoint type: resource metering / admission control
- Sensitive sink: bank cost totals and pack scheduling decisions

## Impact Pattern

- Primary impact: consensus resource accounting
- Secondary impact: none

## Short Reusable Lesson

- The scheduler folded different resource dimensions together too loosely, leaving loaded-account data cost and execution cost out of sync.
