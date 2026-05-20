# Root-Cause Card

## Metadata

- ID: `nibiru-c4-2025-01-mr-m02-transient-gas-meter-removal`
- Bug family: `resource_accounting_and_limits`
- Bug class: `evm-cosmos-gas-meter-semantic-drift`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `EVM-equivalent gas isolation`

## Violated Invariant

- Invariant: EVM gas accounting should remain isolated enough from Cosmos SDK gas accounting to preserve expected EVM gas semantics, or deviations must be explicit and documented.

## Trust Boundary

- Boundary: EVM execution gas model->Cosmos SDK gas meter

## Attack Surface

- Entrypoint type: EthereumTx execution after transient gas meter refactor
- Sensitive sink: combined Cosmos/EVM gas consumption after removing blockGasUsed transient variable

## Impact Pattern

- Primary impact: EVM gas compatibility drift
- Secondary impact: unexpected fee and execution behavior

## Short Reusable Lesson

- A mitigation refactor removed the block/transient gas meter and mixed Cosmos SDK gas with EVM gas, potentially changing gas availability compared with Ethereum.
