# Validation Card

## Metadata

- ID: `nibiru-c4-2024-11-m03-failed-call-gas-accounting`
- Bug family: `resource_accounting_and_limits`
- Bug class: `failed-evm-call-gas-accounting-asymmetry`

## What Confirmed The Issue

- Public C4 report section M-03 rated this as Medium.
- The report or mitigation review links Nibiru remediation PR evidence for this issue class.

## What Could Have Invalidated It

- No issue if callers uniformly consume returned EVM gas for success and failure.
- No issue if transaction format forbids batching and prior gas cannot be reset away.

## Severity Guidance

- Expected impact band: undercharged failed EVM helper calls
- Expected severity band: medium

## False-Positive Cautions

- No issue if callers uniformly consume returned EVM gas for success and failure.
- No issue if transaction format forbids batching and prior gas cannot be reset away.
- No issue if failure always burns the full applicable gas limit.
