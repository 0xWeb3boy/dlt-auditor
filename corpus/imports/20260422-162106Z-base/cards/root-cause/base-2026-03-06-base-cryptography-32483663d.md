# Root-Cause Card

## Metadata

- ID: `base-2026-03-06-base-cryptography-32483663d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: A `ProofClaim` received from the proof transport boundary must be treated as untrusted until structurally validated. The claim should contain at least one proposal, the proposal list should be bounded to prevent resource exhaustion, and each embedded signature blob should match the expected fixed-width wire shape before downstream consumers use the claim.

## Trust Boundary

- Boundary: `proof producer or network peer->verification routine`

## Attack Surface

- Entrypoint type: `proof-or-signature-verification`
- Sensitive sink: `acceptance of a proof, signature, or derived state transition`

## Impact Pattern

- Primary impact: `denial-of-service`
- Secondary impact: `none`

## Short Reusable Lesson

- A `ProofClaim` received from the proof transport boundary must be treated as untrusted until structurally validated. The claim should contain at least one proposal, the proposal list should be bounded to prevent resource exhaustion, and each embedded signature blob should match the expected fixed-width wire shape before downstream consumers use the claim. The refactor changed `ProofClaim` from a small fixed-shape record into a container holding nested proposal objects and a variable-length vector coming from an untrusted boundary. The supported issue is missing structural validation of that new untrusted shape, especially unbounded collection size and malformed signature blobs. The robust fix is to make the privileged sink consume the same canonical state, identity, or proof representation that was actually validated and fail closed when that binding is missing.
