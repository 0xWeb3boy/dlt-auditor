# Root-Cause Card

## Metadata

- ID: `go-ethereum-2021-07-22-go-ethereum-transaction-processing-97aacd9b3`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `transaction-balance-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `consensus-validation`

## Violated Invariant

- Invariant: For London/EIP-1559 transactions, the sender balance checked before state mutation must cover the maximum gas liability, gas_limit * gasFeeCap, plus the transaction value when that value has not yet been deducted.

## Trust Boundary

- Boundary: Untrusted RPC or debug request parameters reaching privileged node logic.

## Attack Surface

- Entrypoint type: `rpc method`
- Sensitive sink: `expensive RPC-side computation, allocation, or response construction`

## Impact Pattern

- Primary impact: `consensus-state-transition-integrity`
- Secondary impact: `validation-bypass`

## Short Reusable Lesson

- The patch corrects go-ethereum's London/EIP-1559 upfront balance check.
