# Root-Cause Card

## Metadata

- ID: `base-2026-01-22-base-transaction-processing-13a095daa`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incorrect-cache-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `state-coordinate-consistency`

## Violated Invariant

- Invariant: Cached execution should only be reused when it was derived from the same parent block context and the same ordered prefix of prior transaction hashes; otherwise cached results must be rejected.

## Trust Boundary

- Boundary: `transaction, batch, or proof input->execution or derivation pipeline`

## Attack Surface

- Entrypoint type: `transaction-or-batch-validation`
- Sensitive sink: `reuse of cached checkpoint or execution data that drives proposer or validator actions`

## Impact Pattern

- Primary impact: `state-integrity`
- Secondary impact: `none`

## Short Reusable Lesson

- Cached execution should only be reused when it was derived from the same parent block context and the same ordered prefix of prior transaction hashes; otherwise cached results must be rejected. An inverted condition in the cached-execution guard caused the validator to key rejection off a successful transaction-prefix comparison instead of a mismatch. The iterator-signature and cache-hydration changes appear to support the corrected flow rather than show a separate root cause. The robust fix is to make the privileged sink consume the same canonical state, identity, or proof representation that was actually validated and fail closed when that binding is missing.
