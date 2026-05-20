# Validation Card

## Metadata

- ID: `nibiru-c4-2024-11-m10-oracle-stale-timestamp`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `oracle-price-timestamp-freshness-misbinding`

## What Confirmed The Issue

- Public C4 report section M-10 rated this as Medium.
- The report or mitigation review links Nibiru remediation PR evidence for this issue class.

## What Could Have Invalidated It

- No issue if the timestamp is persisted with the price update.
- No issue if consumers do not use the timestamp for freshness and docs say so clearly.

## Severity Guidance

- Expected impact band: stale oracle price accepted as fresh
- Expected severity band: medium

## False-Positive Cautions

- No issue if the timestamp is persisted with the price update.
- No issue if consumers do not use the timestamp for freshness and docs say so clearly.
- No issue if stale prices are impossible due to independent oracle expiry enforcement.
