# Code-Shape Card

Record: `omni-cantina-m06-l1-bridge-balance-stale-overwrite`
Project: `omni-network`
Source finding: `Omni Cantina M-6`

## Search Shape

One bridge direction sends delayed absolute reserve snapshots while the opposite direction consumes the same mirror as a local liquidity limit.

## Motifs

- `l1BridgeBalance = l1Balance`
- `amount <= l1BridgeBalance`
- `l1BridgeBalance decrement`
- `12 minutes L1 to L2`
- `5 to 10 seconds L2 to L1`
- `insufficient token balance`
- `claimable only native withdraw failure`

## Negative Signals

- Updates are deltas instead of absolute overwrites.
- Snapshots include freshness or sequence checks.
- Failed L1 withdrawals refund the Native source funds.

## Likely Fix Shape

Use delta or causally ordered reserve accounting, reject stale snapshots, track pending withdrawals, and refund source funds on failed destination settlement.
