# Code-Shape Card

## Metadata

- ID: `nibiru-2025-01-06-nibiru-transaction-processing-350b9e97`
- Bug family: `resource_accounting_and_limits`
- Bug class: `gas-accounting-undercharge`

## Code Shape Summary

- A gas invariant wrapper measured bank operations under zero-cost store gas settings and then charged the real transaction meter from that discounted measurement.

## Search Motifs

- WithKVGasConfig(zeroCostGasConfig)
- substitute gas meter used for measurement
- ForceGasInvariant charges original meter after wrapped operation
- tests change expected gas from zero/low to non-zero/higher

## Typical Asymmetry

- The trusted protocol side assumes a helper, callback, registry, iterator, or accounting result is already safe; the attacker controls the input, callee, ordering, or transaction shape that reaches that trusted sink.

## Patch Pattern

- Measure wrapped work without zero-cost store configs, avoid premature exhaustion with an infinite substitute meter, and assert non-zero measured gas in tests.

## False Match Warnings

- Do not flag test-only gas meters
- InfiniteGasMeter can be correct when used only to avoid double charging while preserving store gas configs
- Need evidence that measured gas is later charged to the user transaction
