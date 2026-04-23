# Code-Shape Card

## Metadata

- ID: `go-ethereum-2021-07-22-go-ethereum-transaction-processing-97aacd9b3`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `transaction-balance-validation`

## Code Shape Summary

- The EIP-1559 balance precheck in StateTransition.buyGas was incomplete for go-ethereum's execution order: it performed the balance comparison before deducting the transfer value, but did not include that value in the upfront required balance.

## Search Motifs

- Motif 1: rpc method missing exact checks for transaction balance validation
- Motif 2: security-sensitive path reaches expensive RPC-side computation, allocation, or response construction before rejecting malformed or unauthorized input
- Motif 3: Include all not-yet-deducted liabilities in upfront transaction affordability checks before comparing sender balance against the required amount

## Typical Asymmetry

- A cheap caller-controlled request dimension can scale expensive local computation, allocation, or persistent side effects.

## Patch Pattern

- Include all not-yet-deducted liabilities in upfront transaction affordability checks before comparing sender balance against the required amount.

## False Match Warnings

- Classify as EIP-1559 transaction balance validation, not replay or signature validation.
- Treat the impact as consensus/state-transition integrity risk, not proven direct asset theft.
