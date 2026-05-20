# Code-Shape Card

## Metadata

- ID: `nibiru-c4-2024-11-m04-cumulative-gas-refund`
- Bug family: `resource_accounting_and_limits`
- Bug class: `cumulative-gas-refund-miscalculation`

## Code Shape Summary

- Refund logic compared evmMsg.Gas to a cumulative blockGasUsed value, causing later messages to inherit earlier gas usage in their refund calculation.

## Search Motifs

- refundGas uses blockGasUsed
- evmMsg.Gas greater than cumulative gas
- gas charged by txData.Fee
- proper tx gas refund outside CallContract

## Typical Asymmetry

- The trusted protocol side assumes a helper, cache, callback, token, meter, or account state is already safe; the attacker controls the input, ordering, token behavior, query, or nested call that reaches the trusted sink.

## Patch Pattern

- Calculate refunds from each EVM message gas limit minus that message actual gas used, with cumulative gas used only for transaction-level metering.

## False Match Warnings

- No issue if fee deduction is explicitly based on the same aggregate batch gas unit.
- No issue if only one EVM message can exist per transaction.
- No issue if cumulative gas is never used in per-message refund math.
