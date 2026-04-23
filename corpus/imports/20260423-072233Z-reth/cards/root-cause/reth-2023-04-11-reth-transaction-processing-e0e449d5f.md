# Root-Cause Card

## Metadata

- ID: `reth-2023-04-11-reth-transaction-processing-e0e449d5f`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-input-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `signer-authorization`

## Violated Invariant

- Invariant: TODO

## Trust Boundary

- Boundary: TODO

## Attack Surface

- Entrypoint type: TODO
- Sensitive sink: TODO

## Impact Pattern

- Primary impact: TODO
- Secondary impact: TODO

## Short Reusable Lesson

- The patch tightens legacy Ethereum signature decoding in `crates/primitives/src/transaction/signature.rs` by rejecting non-`27`/`28` legacy `v` values. That is a concrete validation improvement in a security-sensitive parser, but the provided evidence does not establish a specific exploit, consensus issue, replay issue, or signature forgery bug.
