# Root-Cause Card

## Metadata

- ID: `optimism-2024-10-18-optimism-cryptography-cc4527008e`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `state-validation-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: Cross-safe checks should derive their L1 scope from the exact next eligible cross-safe candidate and reject inconsistent local-safe/cross-safe DB state instead of inferring scope from a broader local-safe lookup.

## Trust Boundary

- Boundary: external proof/data provider -> verifier/derivation code

## Attack Surface

- Entrypoint type: proof-or-data-verification path
- Sensitive sink: acceptance of cryptographic, blob, preimage, or proof data into derivation/state

## Impact Pattern

- Primary impact: integrity
- Secondary impact: state-integrity

## Short Reusable Lesson

- Cross-safe checks should derive their L1 scope from the exact next eligible cross-safe candidate and reject inconsistent local-safe/cross-safe DB state instead of inferring scope from a broader local-safe lookup. Similar bugs appear when proof-or-data-verification path code treats partially checked input as authoritative and lets it reach acceptance of cryptographic, blob, preimage, or proof data into derivation/state. The reusable fix is to enforce input-validation at the boundary and fail closed before state, privilege, or consensus-visible output changes.
