# Root-Cause Card

## Metadata

- ID: `base-2024-06-27-base-cryptography-bfe0dd435`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `verification-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `canonical-verification`

## Violated Invariant

- Invariant: If oracle cache entries are security-relevant, verification should operate on canonical `PreimageKey` values and, for precompile-backed entries, ensure the stored output matches the decoded precompile invocation derived from associated hint data.

## Trust Boundary

- Boundary: `proof producer or network peer->verification routine`

## Attack Surface

- Entrypoint type: `proof-or-signature-verification`
- Sensitive sink: `acceptance of a proof, signature, or derived state transition`

## Impact Pattern

- Primary impact: `integrity-hardening`
- Secondary impact: `none`

## Short Reusable Lesson

- If oracle cache entries are security-relevant, verification should operate on canonical `PreimageKey` values and, for precompile-backed entries, ensure the stored output matches the decoded precompile invocation derived from associated hint data. The visible root issue is incomplete or less explicit verification logic in the oracle validation path, especially for `PreimageKeyType::Precompile`. However, the evidence also shows routine type-conversion adjustments, so the patch does not cleanly isolate a proven security bug as opposed to correctness or implementation completion work. The robust fix is to make the privileged sink consume the same canonical state, identity, or proof representation that was actually validated and fail closed when that binding is missing.
