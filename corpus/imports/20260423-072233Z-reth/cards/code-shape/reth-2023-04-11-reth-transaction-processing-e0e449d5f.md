# Code-Shape Card

## Metadata

- ID: `reth-2023-04-11-reth-transaction-processing-e0e449d5f`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-input-validation`

## Code Shape Summary

- The patch tightens legacy Ethereum signature decoding in `crates/primitives/src/transaction/signature.rs` by rejecting non-`27`/`28` legacy `v` values. That is a concrete validation improvement in a security-sensitive parser, but the provided evidence does not establish a specific exploit, consensus issue, replay issue, or signature forgery bug.

## Search Motifs

- Motif 1: TODO
- Motif 2: TODO
- Motif 3: TODO

## Typical Asymmetry

- TODO

## Patch Pattern

- TODO

## False Match Warnings

- TODO
