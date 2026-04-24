# Root-Cause Card

## Metadata

- ID: `reth-2023-04-11-reth-transaction-processing-e0e449d5f`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-input-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `signature-field-validation`

## Violated Invariant

- Invariant: Ethereum signature decoding should preserve the canonical `v` encoding used by the scheme: EIP-155 values use `35 + 2*chain_id + parity`, and legacy values use only `27` or `28`. The decoder should reject other legacy `v` values rather than coercing them into a parity bit.

## Trust Boundary

- Boundary: externally supplied transaction bytes -> signer recovery

## Attack Surface

- Entrypoint type: transaction-signature-decoder
- Sensitive sink: authenticated transaction sender identity

## Impact Pattern

- Primary impact: acceptance-of-malformed-input
- Secondary impact: signature-validation-bypass

## Short Reusable Lesson

- Ethereum signature decoding should preserve the canonical `v` encoding used by the scheme: EIP-155 values use `35 + 2*chain_id + parity`, and legacy values use only `27` or `28`. The decoder should reject other legacy `v` values rather than coercing them into a parity bit.
