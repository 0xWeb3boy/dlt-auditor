# Root-Cause Card

## Metadata

- ID: `nibiru-c4-2024-11-m03-failed-call-gas-accounting`
- Bug family: `resource_accounting_and_limits`
- Bug class: `failed-evm-call-gas-accounting-asymmetry`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `success-failure gas accounting symmetry`

## Violated Invariant

- Invariant: Every EVM call outcome inside a transaction must charge the Cosmos gas meter for the actual EVM gas consumed without resetting away earlier message gas.

## Trust Boundary

- Boundary: user transaction->EVM CallContract helper->Cosmos gas meter

## Attack Surface

- Entrypoint type: EVM CallContractWithInput helper
- Sensitive sink: ResetGasMeterAndConsumeGas and transient/cumulative EVM gas tracking

## Impact Pattern

- Primary impact: undercharged failed EVM helper calls
- Secondary impact: incorrect block/transaction gas accounting

## Short Reusable Lesson

- The failure branch reset the gas meter with only the failed evmResp.GasUsed, while success and caller paths used different cumulative accounting rules.
