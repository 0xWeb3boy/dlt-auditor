# Root-Cause Card

## Metadata

- ID: `nibiru-c4-2025-01-mr-h03-funtoken-conversion-unmetered-evm-calls`
- Bug family: `resource_accounting_and_limits`
- Bug class: `cosmos-message-evm-call-gas-not-consumed`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `cross-engine gas propagation`

## Violated Invariant

- Invariant: Cosmos messages that invoke EVM calls must consume the EVM gas used by those calls in the Cosmos SDK gas meter.

## Trust Boundary

- Boundary: Cosmos tx message->embedded EVM contract call

## Attack Surface

- Entrypoint type: MsgCreateFunToken or MsgConvertCoinToEvm
- Sensitive sink: ERC20 metadata, transfer, and conversion CallContract gas usage

## Impact Pattern

- Primary impact: unmetered EVM work from Cosmos messages
- Secondary impact: resource-exhaustion fee bypass

## Short Reusable Lesson

- MsgConvertCoinToEvm and MsgCreateFunToken performed ERC20 EVM calls for transfer or metadata retrieval without reliably charging the Cosmos gas meter for that EVM work.
