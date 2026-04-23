# Root-Cause Card

## Metadata

- ID: `go-ethereum-2021-07-22-go-ethereum-transaction-processing-97aacd9b3`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `transaction-balance-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: TODO

## Trust Boundary

- Boundary: TODO

## Attack Surface

- Entrypoint type: TODO
- Sensitive sink: TODO

## Impact Pattern

- Primary impact: TODO
- Secondary impact: TODO

## Short Reusable Lesson

- The patch corrects go-ethereum's London/EIP-1559 upfront balance check. In StateTransition.buyGas, the EIP-1559 balance requirement previously included gas_limit * gasFeeCap but omitted the transaction value. The fix adds st.value before comparing the sender balance to the required amount. This is best classified as a likely security-relevant consensus/state-transition validation fix, not as replay, signature, or cryptographic handling.
