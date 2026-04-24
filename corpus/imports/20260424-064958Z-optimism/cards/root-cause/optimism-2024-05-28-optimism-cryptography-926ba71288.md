# Root-Cause Card

## Metadata

- ID: `optimism-2024-05-28-optimism-cryptography-926ba71288`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: Plasma DA must use one explicit commitment mode end to end. The configured commitment type must be a supported value, runtime config must carry that type, incoming commitments must match it, keccak mode requires a challenge-contract address, and generic mode must not use that address.

## Trust Boundary

- Boundary: external proof/data provider -> verifier/derivation code

## Attack Surface

- Entrypoint type: proof-or-data-verification path
- Sensitive sink: acceptance of cryptographic, blob, preimage, or proof data into derivation/state

## Impact Pattern

- Primary impact: integrity
- Secondary impact: state-integrity

## Short Reusable Lesson

- Plasma DA must use one explicit commitment mode end to end. The configured commitment type must be a supported value, runtime config must carry that type, incoming commitments must match it, keccak mode requires a challenge-contract address, and generic mode must not use that address. Similar bugs appear when proof-or-data-verification path code treats partially checked input as authoritative and lets it reach acceptance of cryptographic, blob, preimage, or proof data into derivation/state. The reusable fix is to enforce input-validation at the boundary and fail closed before state, privilege, or consensus-visible output changes.
