# Root-Cause Card

## Metadata

- ID: `optimism-2025-11-24-optimism-consensus-b2d4a686db`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `protocol-invariant-enforcement`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: A deposit-only payload derivation path should not pass through non-deposit transactions when constructing the payload attributes used by downstream engine logic.

## Trust Boundary

- Boundary: remote or persisted chain signal -> consensus state machine

## Attack Surface

- Entrypoint type: forkchoice/finality state-transition path
- Sensitive sink: safe/finalized head promotion, rewind, or consensus checkpoint update

## Impact Pattern

- Primary impact: protocol-integrity-risk
- Secondary impact: consensus-integrity

## Short Reusable Lesson

- A deposit-only payload derivation path should not pass through non-deposit transactions when constructing the payload attributes used by downstream engine logic. Similar bugs appear when forkchoice/finality state-transition path code treats partially checked input as authoritative and lets it reach safe/finalized head promotion, rewind, or consensus checkpoint update. The reusable fix is to enforce input-validation at the boundary and fail closed before state, privilege, or consensus-visible output changes.
