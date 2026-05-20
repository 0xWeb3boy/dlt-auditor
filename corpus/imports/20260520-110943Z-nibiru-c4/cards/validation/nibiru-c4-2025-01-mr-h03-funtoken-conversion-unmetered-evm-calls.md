# Validation Card

## Metadata

- ID: `nibiru-c4-2025-01-mr-h03-funtoken-conversion-unmetered-evm-calls`
- Bug family: `resource_accounting_and_limits`
- Bug class: `cosmos-message-evm-call-gas-not-consumed`

## What Confirmed The Issue

- Public C4 report section MR-H-03 rated this as High.
- The report or mitigation review links Nibiru remediation PR evidence for this issue class.

## What Could Have Invalidated It

- No issue if the path runs inside EthereumTx and charges caller gas there.
- No issue if every CallContract caller consumes returned gas in the SDK meter.

## Severity Guidance

- Expected impact band: unmetered EVM work from Cosmos messages
- Expected severity band: high

## False-Positive Cautions

- No issue if the path runs inside EthereumTx and charges caller gas there.
- No issue if every CallContract caller consumes returned gas in the SDK meter.
- No issue if only constant-time trusted metadata reads are possible.
