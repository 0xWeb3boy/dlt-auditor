# Validation Card

## Metadata

- ID: `nibiru-c4-2024-11-h06-funtoken-recursive-gas-forwarding`
- Bug family: `resource_accounting_and_limits`
- Bug class: `recursive-gas-forwarding`

## What Confirmed The Issue

- Public C4 report section H-06 rated this as High.
- The report or mitigation review links Nibiru remediation PR evidence for this issue class.

## What Could Have Invalidated It

- No issue if internal calls use at most 63/64 of remaining caller gas.
- No issue if the callee ERC20 is trusted and non-reentrant by construction.

## Severity Guidance

- Expected impact band: block production halt through recursive precompile calls
- Expected severity band: high

## False-Positive Cautions

- No issue if internal calls use at most 63/64 of remaining caller gas.
- No issue if the callee ERC20 is trusted and non-reentrant by construction.
- No issue if recursion depth and memory growth are bounded by charged caller gas.
