# Code-Shape Card

## Metadata

- ID: `nibiru-c4-2024-11-m10-oracle-stale-timestamp`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `oracle-price-timestamp-freshness-misbinding`

## Code Shape Summary

- queryExchangeRate passed through a blockTime derived from current query context rather than persisted update-time metadata for the exchange rate.

## Search Motifs

- GetDatedExchangeRate returns current block time
- queryExchangeRate blockTimeMs
- oracle price timestamp missing from storage
- staleness check always current block

## Typical Asymmetry

- The trusted protocol side assumes a helper, cache, callback, token, meter, or account state is already safe; the attacker controls the input, ordering, token behavior, query, or nested call that reaches the trusted sink.

## Patch Pattern

- Persist the block timestamp alongside each exchange rate update and return that stored timestamp from the precompile.

## False Match Warnings

- No issue if the timestamp is persisted with the price update.
- No issue if consumers do not use the timestamp for freshness and docs say so clearly.
- No issue if stale prices are impossible due to independent oracle expiry enforcement.
