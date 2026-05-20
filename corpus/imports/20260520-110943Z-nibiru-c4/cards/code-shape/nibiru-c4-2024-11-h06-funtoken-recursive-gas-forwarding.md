# Code-Shape Card

## Metadata

- ID: `nibiru-c4-2024-11-h06-funtoken-recursive-gas-forwarding`
- Bug family: `resource_accounting_and_limits`
- Bug class: `recursive-gas-forwarding`

## Code Shape Summary

- FunToken ERC20 BalanceOf and Transfer helpers used fixed gas limits for nested EVM calls, allowing recursive calls to receive fresh gas repeatedly.

## Search Motifs

- Erc20GasLimitQuery hardcoded 100_000
- Erc20GasLimitExecute
- CallContract inside precompile with fixed gas
- ERC20 balanceOf recursively calls precompile
- 63/64 gas invariant broken

## Typical Asymmetry

- The trusted protocol side assumes a helper, cache, callback, token, meter, or account state is already safe; the attacker controls the input, ordering, token behavior, query, or nested call that reaches the trusted sink.

## Patch Pattern

- Forward a caller-relative gas budget to ERC20 helper calls and preserve EIP-150-style gas reduction for nested precompile/EVM recursion.

## False Match Warnings

- No issue if internal calls use at most 63/64 of remaining caller gas.
- No issue if the callee ERC20 is trusted and non-reentrant by construction.
- No issue if recursion depth and memory growth are bounded by charged caller gas.
