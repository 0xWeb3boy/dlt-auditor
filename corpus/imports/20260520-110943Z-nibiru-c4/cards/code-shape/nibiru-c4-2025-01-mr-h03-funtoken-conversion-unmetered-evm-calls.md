# Code-Shape Card

## Metadata

- ID: `nibiru-c4-2025-01-mr-h03-funtoken-conversion-unmetered-evm-calls`
- Bug family: `resource_accounting_and_limits`
- Bug class: `cosmos-message-evm-call-gas-not-consumed`

## Code Shape Summary

- MsgConvertCoinToEvm and MsgCreateFunToken performed ERC20 EVM calls for transfer or metadata retrieval without reliably charging the Cosmos gas meter for that EVM work.

## Search Motifs

- convertCoinToEvmBornERC20 does not consume evm gas
- createFunTokenFromERC20 metadata CallContract
- CallContractWithInput gas used return ignored
- consume gas in CallContractWithInput

## Typical Asymmetry

- The trusted protocol side assumes a helper, cache, callback, token, meter, or account state is already safe; the attacker controls the input, ordering, token behavior, query, or nested call that reaches the trusted sink.

## Patch Pattern

- Make CallContractWithInput or its callers consume EVM gas in the Cosmos SDK gas meter for both metadata and conversion call paths.

## False Match Warnings

- No issue if the path runs inside EthereumTx and charges caller gas there.
- No issue if every CallContract caller consumes returned gas in the SDK meter.
- No issue if only constant-time trusted metadata reads are possible.
