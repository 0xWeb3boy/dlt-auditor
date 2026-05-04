# Code-Shape Card

## Metadata

- ID: `moonbeam-2026-02-21-moonbeam-transaction-processing-8cff9775f9`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `unprotected-transaction-admission`

## Code Shape Summary

- A production runtime allowed unprotected legacy Ethereum transactions by configuration. The fix sets AllowUnprotectedTxs false and aligns RPC/tests with protected transaction requirements.

## Search Motifs

- AllowUnprotectedTxs true across multiple runtimes
- legacy Ethereum transactions accepted without chain id
- RPC admission flag for unprotected txs changed to false

## Typical Asymmetry

- The accepting path trusted a local or current-state predicate, while the sensitive sink required a stronger global, historical, caller-class, domain, or cumulative invariant.

## Patch Pattern

- Set transaction-admission policy to reject unprotected legacy transactions consistently across runtime and node RPC code.

## False Match Warnings

- Dev runtimes may allow unprotected txs for local testing
- Presence of legacy transaction support is not a bug if chain-id is required
- Replay risk is lower if signatures are domain-bound elsewhere
