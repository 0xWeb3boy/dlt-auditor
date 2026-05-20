# Validation Card

## Metadata

- ID: `nibiru-c4-2024-11-m06-tracetx-unbounded-predecessors`
- Bug family: `resource_accounting_and_limits`
- Bug class: `unbounded-rpc-simulation-work`

## What Confirmed The Issue

- Public C4 report section M-06 rated this as Medium.
- The report kept this as a non-low finding without a confirmed mitigation PR in the included mitigation scope.

## What Could Have Invalidated It

- No issue if the endpoint is authenticated or operator-local only.
- No issue if request size, predecessor count, total gas, and timeout are already bounded.

## Severity Guidance

- Expected impact band: RPC resource exhaustion
- Expected severity band: medium

## False-Positive Cautions

- No issue if the endpoint is authenticated or operator-local only.
- No issue if request size, predecessor count, total gas, and timeout are already bounded.
- No chain-wide issue unless validators expose the endpoint in a way that affects consensus.
