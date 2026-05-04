# Code-Shape Card

## Metadata

- ID: `stellar-core-2017-04-24-stellar-core-transaction-processing-00515f37c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `protocol-accounting-invariant`

## Code Shape Summary

- The inflation path computed a payout pool from minted inflation plus existing fees, then updated the aggregate coin counter using payout behavior rather than the minted component alone.

## Search Motifs

- totalCoins incremented inside payout loop
- feePool added to inflation amount
- inflationAmount separated from amountToDole
- ledger version gated monetary accounting fix

## Typical Asymmetry

- The code had a validation or resource-control assumption at one boundary, but a later authoritative boundary or helper accepted broader state than the invariant allowed.
- The risky input was ordinary protocol data or operator configuration, so the bug shape looks like normal processing until the missing property is checked against the sensitive sink.

## Patch Pattern

- Separate minted value from redistributed value and update aggregate supply exactly once from the minted component under new protocol-version rules.

## False Match Warnings

- Redistribution of existing fees is valid if supply counters are unchanged.
- Legacy ledger-version gates may intentionally preserve historical behavior.
- Accounting-display fixes are lower risk if consensus state is unaffected.
