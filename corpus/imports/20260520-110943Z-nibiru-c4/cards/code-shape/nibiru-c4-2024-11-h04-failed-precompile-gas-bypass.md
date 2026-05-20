# Code-Shape Card

## Metadata

- ID: `nibiru-c4-2024-11-h04-failed-precompile-gas-bypass`
- Bug family: `resource_accounting_and_limits`
- Bug class: `failed-precompile-gas-undercharge`

## Code Shape Summary

- Precompile handlers returned immediately on err and only called contract.UseGas after the success path.

## Search Motifs

- if err != nil return before contract.UseGas
- CacheCtx.GasMeter().GasConsumed()
- precompile method failure path
- Wasm execute fails after consuming gas

## Typical Asymmetry

- The trusted protocol side assumes a helper, cache, callback, token, meter, or account state is already safe; the attacker controls the input, ordering, token behavior, query, or nested call that reaches the trusted sink.

## Patch Pattern

- Consume the cached/native gas before returning any precompile error, commonly via defer or by moving contract.UseGas ahead of error handling.

## False Match Warnings

- No issue if gas is consumed in a defer for both success and failure.
- No issue if the failed call performs no meaningful metered work.
- No issue if outer logic always charges the full gas limit on precompile failure.
