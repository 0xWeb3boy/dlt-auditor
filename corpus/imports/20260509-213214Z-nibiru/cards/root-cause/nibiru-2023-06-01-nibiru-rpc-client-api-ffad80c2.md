# Root-Cause Card

## Metadata

- ID: `nibiru-2023-06-01-nibiru-rpc-client-api-ffad80c2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-margin-ratio-check`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `post-withdrawal collateralization check`

## Violated Invariant

- Invariant: Any margin withdrawal or position mutation must validate the resulting position against liquidation thresholds before releasing collateral or committing state.

## Trust Boundary

- Boundary: Trader-controlled margin operation crosses into vault withdrawal and collateral accounting.

## Attack Surface

- Entrypoint type: state-changing margin removal / position update transaction
- Sensitive sink: vault withdrawal and persisted position margin state

## Impact Pattern

- Primary impact: undercollateralized withdrawals
- Secondary impact: economic distortion and bad debt

## Short Reusable Lesson

- A margin-removal path needed a shared final-state collateralization check before vault withdrawal. The pattern is missing invariant enforcement after applying funding and margin deltas.
