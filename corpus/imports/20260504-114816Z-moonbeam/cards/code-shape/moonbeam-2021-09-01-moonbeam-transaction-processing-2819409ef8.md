# Code-Shape Card

## Metadata

- ID: `moonbeam-2021-09-01-moonbeam-transaction-processing-2819409ef8`
- Bug family: `resource_accounting_and_limits`
- Bug class: `fee-accounting-mismatch`

## Code Shape Summary

- The EVM runtime configuration used a no-op fee hook while Substrate transactions used DealWithFees. The fix wires EVMCurrencyAdapter and adds the EVM callback for nonzero imbalances.

## Search Motifs

- OnChargeTransaction = () in an EVM runtime config
- separate fee handlers for EVM and native transaction paths
- on_unbalanceds implemented but on_nonzero_unbalanced missing for another execution path

## Typical Asymmetry

- The accepting path trusted a local or current-state predicate, while the sensitive sink required a stronger global, historical, caller-class, domain, or cumulative invariant.

## Patch Pattern

- Attach the EVM execution path to the same currency adapter and burn/treasury imbalance policy used by native transactions.

## False Match Warnings

- A no-op hook may be safe in tests or fee-free dev networks
- Fees may be charged earlier by a separate mandatory adapter
- Distribution-only differences are lower severity if total fees are still collected
