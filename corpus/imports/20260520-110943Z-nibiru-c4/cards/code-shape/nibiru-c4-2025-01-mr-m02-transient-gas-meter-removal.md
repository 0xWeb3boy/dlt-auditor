# Code-Shape Card

## Metadata

- ID: `nibiru-c4-2025-01-mr-m02-transient-gas-meter-removal`
- Bug family: `resource_accounting_and_limits`
- Bug class: `evm-cosmos-gas-meter-semantic-drift`

## Code Shape Summary

- A mitigation refactor removed the block/transient gas meter and mixed Cosmos SDK gas with EVM gas, potentially changing gas availability compared with Ethereum.

## Search Motifs

- removed blockGasUsed transient variable
- block transient gas meter removed
- Cosmos SDK gas and EVM gas mixed
- EVM gas compatibility issue

## Typical Asymmetry

- The trusted protocol side assumes a helper, cache, callback, token, meter, or account state is already safe; the attacker controls the input, ordering, token behavior, query, or nested call that reaches the trusted sink.

## Patch Pattern

- Restore an EVM-specific transient gas meter or document and regression-test the intentional gas semantic difference from Ethereum.

## False Match Warnings

- No issue if the chain intentionally documents and tests non-Ethereum gas semantics.
- No issue if a replacement isolation model preserves EVM gas equivalence.
- No issue if the removed meter was dead code and all observable gas remains unchanged.
