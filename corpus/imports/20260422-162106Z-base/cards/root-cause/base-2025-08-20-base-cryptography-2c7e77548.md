# Root-Cause Card

## Metadata

- ID: `base-2025-08-20-base-cryptography-2c7e77548`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-verification-check`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `verification-result-handling`

## Violated Invariant

- Invariant: Blob data should be accepted only if batch KZG verification succeeds with an explicit `Ok(true)` result. An `Ok(false)` verification result must be treated as failure, not as success.

## Trust Boundary

- Boundary: `proof producer or network peer->verification routine`

## Attack Surface

- Entrypoint type: `transaction-or-batch-validation`
- Sensitive sink: `acceptance of a proof, signature, or derived state transition`

## Impact Pattern

- Primary impact: `invalid-proof-acceptance`
- Secondary impact: `integrity-risk`

## Short Reusable Lesson

- Blob data should be accepted only if batch KZG verification succeeds with an explicit `Ok(true)` result. An `Ok(false)` verification result must be treated as failure, not as success. The root cause is misuse of a verification API that reports semantic failure as `Ok(false)` rather than `Err(...)`. The pre-patch code checked only for API error propagation and ignored the boolean verification outcome. The robust fix is to make the privileged sink consume the same canonical state, identity, or proof representation that was actually validated and fail closed when that binding is missing.
