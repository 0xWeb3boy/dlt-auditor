# Root-Cause Card

## Metadata

- ID: `go-ethereum-2026-03-24-go-ethereum-transaction-processing-8327e870e`
- Bug family: `resource_accounting_and_limits`
- Bug class: `gas-accounting-ordering`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `resource-accounting`

## Violated Invariant

- Invariant: For EIP-8037 two-dimensional gas accounting, regular gas and state gas must be charged in the intended order, with regular-gas out-of-gas handling occurring before state-gas accounting that the patch comments describe as able to inflate a reservoir.

## Trust Boundary

- Boundary: Untrusted transaction data crossing into local execution and admission checks.

## Attack Surface

- Entrypoint type: `transaction validation path`
- Sensitive sink: `consensus-visible state transition or journal replay`

## Impact Pattern

- Primary impact: `resource-accounting`
- Secondary impact: `protocol-resource-control`

## Short Reusable Lesson

- The patch changes EIP-8037 gas accounting in SSTORE and CALL-family paths so regular gas is charged before state gas, and adjusts parallel receipt aggregation to separate execution cumulative gas from regular/state gas totals.
