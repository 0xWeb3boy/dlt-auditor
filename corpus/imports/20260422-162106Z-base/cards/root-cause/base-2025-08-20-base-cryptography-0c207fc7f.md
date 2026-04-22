# Root-Cause Card

## Metadata

- ID: `base-2025-08-20-base-cryptography-0c207fc7f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-verification`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `verification-result-handling`

## Violated Invariant

- Invariant: Blob data must not be accepted into `BlobStore` unless batch KZG verification returns an explicit success result, `Ok(true)`.

## Trust Boundary

- Boundary: `proof producer or network peer->verification routine`

## Attack Surface

- Entrypoint type: `transaction-or-batch-validation`
- Sensitive sink: `acceptance of a proof, signature, or derived state transition`

## Impact Pattern

- Primary impact: `integrity`
- Secondary impact: `none`

## Short Reusable Lesson

- Blob data must not be accepted into `BlobStore` unless batch KZG verification returns an explicit success result, `Ok(true)`. The caller did not fully enforce the verifier's return contract. It treated the absence of an error as sufficient instead of requiring the verifier's explicit success value from a `Result<bool, _>` API. The robust fix is to make the privileged sink consume the same canonical state, identity, or proof representation that was actually validated and fail closed when that binding is missing.
