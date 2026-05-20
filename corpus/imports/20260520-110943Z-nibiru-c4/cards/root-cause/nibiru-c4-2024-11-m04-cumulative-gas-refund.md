# Root-Cause Card

## Metadata

- ID: `nibiru-c4-2024-11-m04-cumulative-gas-refund`
- Bug family: `resource_accounting_and_limits`
- Bug class: `cumulative-gas-refund-miscalculation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `per-message refund accounting`

## Violated Invariant

- Invariant: Gas refunded for one EVM message should be based on that message budget and usage, not unrelated cumulative gas unless the fee was charged for the full batch unit.

## Trust Boundary

- Boundary: EVM transaction submitter->fee deduction and refund logic

## Attack Surface

- Entrypoint type: EthereumTx message execution
- Sensitive sink: refundGas calculation and fee refund transfer

## Impact Pattern

- Primary impact: under-refunded gas fees
- Secondary impact: batched transaction fee surprise

## Short Reusable Lesson

- Refund logic compared evmMsg.Gas to a cumulative blockGasUsed value, causing later messages to inherit earlier gas usage in their refund calculation.
