# Code-Shape Card

## Metadata

- ID: `moonbeam-2026-02-21-moonbeam-transaction-processing-05ce4c8c1a`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `replay-protection-policy-hardening`

## Code Shape Summary

- Runtime constants and RPC setup allowed unprotected legacy Ethereum transactions. The patch flips those booleans to false across networks and updates tests away from legacy txs.

## Search Motifs

- AllowUnprotectedTxs: bool = true in production runtime
- RPC allows unprotected Ethereum transactions
- tests use legacy transaction without chain id

## Typical Asymmetry

- The accepting path trusted a local or current-state predicate, while the sensitive sink required a stronger global, historical, caller-class, domain, or cumulative invariant.

## Patch Pattern

- Disable unprotected transaction acceptance at both runtime configuration and RPC admission boundaries.

## False Match Warnings

- Private/dev chains may intentionally allow legacy unprotected transactions
- Transactions with EIP-155 chain id are not in scope
- A mempool-only flag is lower risk if runtime rejects before inclusion
