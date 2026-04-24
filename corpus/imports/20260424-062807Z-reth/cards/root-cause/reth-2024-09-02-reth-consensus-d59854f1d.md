# Root-Cause Card

## Metadata

- ID: `reth-2024-09-02-reth-consensus-d59854f1d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-runtime-bound-check`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `numeric-bound-validation`

## Violated Invariant

- Invariant: In `TreeState::remove_until`, the effective finalized bound used for pruning should not exceed the caller's `upper_bound`. If `finalized_num` is higher, removal should behave as though the finalized bound were `upper_bound`, rather than trusting the caller-provided value.

## Trust Boundary

- Boundary: consensus layer signal -> execution client forkchoice/block state

## Attack Surface

- Entrypoint type: engine-api/forkchoice-handler
- Sensitive sink: canonical head, payload status, or pipeline scheduling

## Impact Pattern

- Primary impact: incorrect-state-pruning
- Secondary impact: consensus-integrity

## Short Reusable Lesson

- In `TreeState::remove_until`, the effective finalized bound used for pruning should not exceed the caller's `upper_bound`. If `finalized_num` is higher, removal should behave as though the finalized bound were `upper_bound`, rather than trusting the caller-provided value.
