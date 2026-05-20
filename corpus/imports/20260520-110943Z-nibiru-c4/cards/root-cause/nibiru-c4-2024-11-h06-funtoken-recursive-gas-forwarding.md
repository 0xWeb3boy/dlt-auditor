# Root-Cause Card

## Metadata

- ID: `nibiru-c4-2024-11-h06-funtoken-recursive-gas-forwarding`
- Bug family: `resource_accounting_and_limits`
- Bug class: `recursive-gas-forwarding`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `caller-gas-bounded internal calls`

## Violated Invariant

- Invariant: Internal ERC20 calls made by a precompile must be bounded by remaining caller gas and preserve EVM recursive-call gas limits.

## Trust Boundary

- Boundary: user-controlled ERC20 contract->FunToken precompile internal ERC20 query/transfer

## Attack Surface

- Entrypoint type: FunToken precompile query or conversion call
- Sensitive sink: CallContract using hardcoded ERC20 query or execute gas instead of caller-relative gas

## Impact Pattern

- Primary impact: block production halt through recursive precompile calls
- Secondary impact: unbounded memory growth

## Short Reusable Lesson

- FunToken ERC20 BalanceOf and Transfer helpers used fixed gas limits for nested EVM calls, allowing recursive calls to receive fresh gas repeatedly.
