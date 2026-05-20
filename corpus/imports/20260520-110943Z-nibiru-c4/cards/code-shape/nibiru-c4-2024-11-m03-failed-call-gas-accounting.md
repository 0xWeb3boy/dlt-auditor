# Code-Shape Card

## Metadata

- ID: `nibiru-c4-2024-11-m03-failed-call-gas-accounting`
- Bug family: `resource_accounting_and_limits`
- Bug class: `failed-evm-call-gas-accounting-asymmetry`

## Code Shape Summary

- The failure branch reset the gas meter with only the failed evmResp.GasUsed, while success and caller paths used different cumulative accounting rules.

## Search Motifs

- evmResp.Failed ResetGasMeterAndConsumeGas
- AddToBlockGasUsed only on success
- CallContractWithInput gasUsed not bubbled to caller
- multiple MsgEthereumTx in one SDK tx

## Typical Asymmetry

- The trusted protocol side assumes a helper, cache, callback, token, meter, or account state is already safe; the attacker controls the input, ordering, token behavior, query, or nested call that reaches the trusted sink.

## Patch Pattern

- Bubble EVM gas used to callers and consume it consistently for all outcomes, removing or simplifying the transient gas reset model.

## False Match Warnings

- No issue if callers uniformly consume returned EVM gas for success and failure.
- No issue if transaction format forbids batching and prior gas cannot be reset away.
- No issue if failure always burns the full applicable gas limit.
