# Validation Card

## Metadata

- ID: `nibiru-c4-2025-01-mr-m02-transient-gas-meter-removal`
- Bug family: `resource_accounting_and_limits`
- Bug class: `evm-cosmos-gas-meter-semantic-drift`

## What Confirmed The Issue

- Public C4 report section MR-M-02 rated this as Medium.
- The mitigation review records this as acknowledged; no confirmed fix PR is listed for this issue.

## What Could Have Invalidated It

- No issue if the chain intentionally documents and tests non-Ethereum gas semantics.
- No issue if a replacement isolation model preserves EVM gas equivalence.

## Severity Guidance

- Expected impact band: EVM gas compatibility drift
- Expected severity band: medium

## False-Positive Cautions

- No issue if the chain intentionally documents and tests non-Ethereum gas semantics.
- No issue if a replacement isolation model preserves EVM gas equivalence.
- No issue if the removed meter was dead code and all observable gas remains unchanged.
