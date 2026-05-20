# Root-Cause Card

## Metadata

- ID: `nibiru-c4-2024-11-m10-oracle-stale-timestamp`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `oracle-price-timestamp-freshness-misbinding`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `freshness metadata binding`

## Violated Invariant

- Invariant: Oracle precompile responses must bind price data to the timestamp of the price update, not to the timestamp of the later query block.

## Trust Boundary

- Boundary: native oracle module->EVM contract freshness checks

## Attack Surface

- Entrypoint type: Oracle queryExchangeRate precompile call
- Sensitive sink: blockTimeMs returned to downstream EVM contracts for staleness validation

## Impact Pattern

- Primary impact: stale oracle price accepted as fresh
- Secondary impact: downstream contract mispricing

## Short Reusable Lesson

- queryExchangeRate passed through a blockTime derived from current query context rather than persisted update-time metadata for the exchange rate.
