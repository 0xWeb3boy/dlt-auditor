# Root-Cause Card

## Metadata

- ID: `optimism-2024-05-07-optimism-cryptography-1a9d14b8ab`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-input-validation`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: An online-fetched blob sidecar should only be accepted if it matches the requested IndexedBlobHash for both position and commitment-derived hash; object-internal validity alone is not enough.

## Trust Boundary

- Boundary: external proof/data provider -> verifier/derivation code

## Attack Surface

- Entrypoint type: proof-or-data-verification path
- Sensitive sink: acceptance of cryptographic, blob, preimage, or proof data into derivation/state

## Impact Pattern

- Primary impact: untrusted-data-acceptance
- Secondary impact: security-hardening-or-correctness

## Short Reusable Lesson

- An online-fetched blob sidecar should only be accepted if it matches the requested IndexedBlobHash for both position and commitment-derived hash; object-internal validity alone is not enough. Similar bugs appear when proof-or-data-verification path code treats partially checked input as authoritative and lets it reach acceptance of cryptographic, blob, preimage, or proof data into derivation/state. The reusable fix is to enforce input-validation at the boundary and fail closed before state, privilege, or consensus-visible output changes.
