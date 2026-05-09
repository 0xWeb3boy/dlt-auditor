# Code-Shape Card

## Metadata

- ID: `nibiru-2024-10-24-nibiru-rpc-client-api-dd27f4b6`
- Bug family: `resource_accounting_and_limits`
- Bug class: `evm-gas-resource-control-hardening`

## Code Shape Summary

- A native helper that calls arbitrary contract code was changed to use a fixed gas cap and cached execution context so reverts do not leak state.

## Search Motifs

- CallContract helper computes custom gas from commit context
- comments mention malicious gas-intensive ERC20
- ApplyEvmMsg runs without CacheContext
- gas used unknown on failed contract call

## Typical Asymmetry

- The trusted protocol side assumes a helper, callback, registry, iterator, or accounting result is already safe; the attacker controls the input, callee, ordering, or transaction shape that reaches that trusted sink.

## Patch Pattern

- Use a conservative gas cap for helper contract calls, execute against a cache context, and commit only after successful execution with explicit error handling.

## False Match Warnings

- Do not classify ordinary eth_call gas configuration as security without attacker-controlled contract execution
- Need evidence that helper is reachable from state-changing protocol code
- A cache context alone is not enough if no state mutation can occur
