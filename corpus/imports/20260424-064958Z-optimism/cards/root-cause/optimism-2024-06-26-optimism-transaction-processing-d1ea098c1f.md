# Root-Cause Card

## Metadata

- ID: `optimism-2024-06-26-optimism-transaction-processing-d1ea098c1f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incorrect-proof-state-hash`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `integrity-binding`

## Violated Invariant

- Invariant: Witness-derived hashes used in Cannon proof and trace data should match the encoded VM state for the claimed execution point.

## Trust Boundary

- Boundary: external proof/data provider -> verifier/derivation code

## Attack Surface

- Entrypoint type: proof-or-data-verification path
- Sensitive sink: acceptance of cryptographic, blob, preimage, or proof data into derivation/state

## Impact Pattern

- Primary impact: proof-integrity
- Secondary impact: state-integrity

## Short Reusable Lesson

- Witness-derived hashes used in Cannon proof and trace data should match the encoded VM state for the claimed execution point. Similar bugs appear when proof-or-data-verification path code treats partially checked input as authoritative and lets it reach acceptance of cryptographic, blob, preimage, or proof data into derivation/state. The reusable fix is to enforce integrity-binding at the boundary and fail closed before state, privilege, or consensus-visible output changes.
