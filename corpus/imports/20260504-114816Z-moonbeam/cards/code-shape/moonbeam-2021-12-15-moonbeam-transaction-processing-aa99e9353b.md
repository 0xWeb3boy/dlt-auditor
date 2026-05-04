# Code-Shape Card

## Metadata

- ID: `moonbeam-2021-12-15-moonbeam-transaction-processing-aa99e9353b`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `replay-or-signature-validation`

## Code Shape Summary

- Runtime config exposed reward address operations without visible per-network signature domain constants. The patch added signed origins and network-specific SignatureNetworkIdentifier values.

## Search Motifs

- signature verifier config lacks chain/network identifier
- reward or claim address change authorized by reusable signed message
- same pallet deployed across networks without domain-separated prefix

## Typical Asymmetry

- The accepting path trusted a local or current-state predicate, while the sensitive sink required a stronger global, historical, caller-class, domain, or cumulative invariant.

## Patch Pattern

- Wire authenticated origins and per-network signature domain identifiers into reward authorization runtime configuration.

## False Match Warnings

- Verifier may already include genesis hash, chain id, or pallet-specific domain elsewhere
- Root-only operations before feature activation may not be externally exploitable
- Config-only changes need verifier evidence for confirmed replay claims
