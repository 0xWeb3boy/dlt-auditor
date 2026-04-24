# Root-Cause Card

## Metadata

- ID: `optimism-2024-05-07-optimism-cryptography-4441686d3f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-integrity-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `integrity-binding`

## Violated Invariant

- Invariant: In the online derivation path, a fetched blob sidecar must match the caller's requested IndexedBlobHash by index and expected hash before the blob is accepted.

## Trust Boundary

- Boundary: external proof/data provider -> verifier/derivation code

## Attack Surface

- Entrypoint type: proof-or-data-verification path
- Sensitive sink: acceptance of cryptographic, blob, preimage, or proof data into derivation/state

## Impact Pattern

- Primary impact: state-integrity
- Secondary impact: state-or-proof-integrity

## Short Reusable Lesson

- In the online derivation path, a fetched blob sidecar must match the caller's requested IndexedBlobHash by index and expected hash before the blob is accepted. Similar bugs appear when proof-or-data-verification path code treats partially checked input as authoritative and lets it reach acceptance of cryptographic, blob, preimage, or proof data into derivation/state. The reusable fix is to enforce integrity-binding at the boundary and fail closed before state, privilege, or consensus-visible output changes.
