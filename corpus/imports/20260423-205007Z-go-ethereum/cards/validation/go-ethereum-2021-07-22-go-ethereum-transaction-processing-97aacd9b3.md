# Validation Card

## Metadata

- ID: `go-ethereum-2021-07-22-go-ethereum-transaction-processing-97aacd9b3`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `transaction-balance-validation`

## What Confirmed The Issue

- Evidence 1: core/state_transition.go adds st.value to the EIP-1559 balanceCheck before comparing sender balance.
- Evidence 2: Commit message states EIP-1559 mandates checking sufficient balance for gas * gasFeeCap and explains go-ethereum needed to add value explicitly because balance had not yet been updated.

## What Could Have Invalidated It

- Compensating control 1: Classify as EIP-1559 transaction balance validation, not replay or signature validation.
- Compensating control 2: Treat the impact as consensus/state-transition integrity risk, not proven direct asset theft.

## Severity Guidance

- Expected impact band: high
- Expected severity band: medium

## False-Positive Cautions

- Caution 1: Classify as EIP-1559 transaction balance validation, not replay or signature validation.
- Caution 2: Treat the impact as consensus/state-transition integrity risk, not proven direct asset theft.
