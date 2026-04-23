# Code-Shape Card

## Metadata

- ID: `go-ethereum-2021-07-22-go-ethereum-transaction-processing-97aacd9b3`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `transaction-balance-validation`

## Code Shape Summary

- The patch corrects go-ethereum's London/EIP-1559 upfront balance check. In StateTransition.buyGas, the EIP-1559 balance requirement previously included gas_limit * gasFeeCap but omitted the transaction value. The fix adds st.value before comparing the sender balance to the required amount. This is best classified as a likely security-relevant consensus/state-transition validation fix, not as replay, signature, or cryptographic handling.

## Search Motifs

- Motif 1: TODO
- Motif 2: TODO
- Motif 3: TODO

## Typical Asymmetry

- TODO

## Patch Pattern

- TODO

## False Match Warnings

- TODO
