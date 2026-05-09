# Code-Shape Card

## Metadata

- ID: `nibiru-2024-12-28-nibiru-transaction-processing-1a256f2a`
- Bug family: `resource_accounting_and_limits`
- Bug class: `recursive-gas-forwarding`

## Code Shape Summary

- A recursive ERC20/precompile path now computes forwarded call gas from remaining transaction gas with a 63/64-style cap instead of passing a fresh fixed limit.

## Search Motifs

- CallContract(... Erc20GasLimitExecute) inside mint/burn
- comment mentions EIP-150 or recursive ERC20 precompile calls
- malicious recursive ERC20 regression test
- gas limit not derived from ctx.GasMeter().GasRemaining

## Typical Asymmetry

- The trusted protocol side assumes a helper, callback, registry, iterator, or accounting result is already safe; the attacker controls the input, callee, ordering, or transaction shape that reaches that trusted sink.

## Patch Pattern

- Compute nested call gas from remaining transaction gas, subtract a 1/64 reserve, cap by configured maximum, and add malicious-recursion regression coverage.

## False Match Warnings

- Do not flag single non-recursive helper calls with bounded gas
- Need attacker-controlled callee code or reentry route
- Resource risk should not be reframed as fund theft without evidence
