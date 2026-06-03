# Prompt Family: Invalid Precompile Revert Gas

## Use This For

- Blast native precompile invalid selectors, malformed calldata, revert paths, remaining gas behavior, and zero `RequiredGas`.

## Prompt

```text
Hunt specifically for invalid-selector or malformed-call gas undercharging in the Blast native precompile.

Do not merge this with valid selector `RequiredGas` or high-frame precompile custom surcharge.

Build a selector table:
- calldata shorter than 4 bytes
- unknown 4-byte selector
- valid read selectors
- valid write selectors
- malformed arguments for valid selectors
- unauthorized write selectors
- read-only/static write attempts
- out-of-gas in native execution, if possible

For each case record:
- `RequiredGas(input)`
- whether `Run` executes native reads/writes before returning
- returned error type, especially `ErrExecutionReverted`
- remaining gas after `RunPrecompiledContract`
- whether gas tracker records any precompile gas
- whether caller can repeat the revert path cheaply

Search patterns:
- invalid or unknown selector returns zero `RequiredGas` but still reaches selector parsing, error construction, or revert handling
- `ErrExecutionReverted` returns remaining gas differently from ordinary precompile failure
- malformed calldata consumes client work but no precompile gas
- validation treats the valid-selector undercharge as covering invalid-selector revert gas and drops the separate issue

Questions to answer:
1. Does an invalid selector consume any fixed precompile gas?
2. Does it revert after any attacker-controlled native work or parsing effort?
3. Is remaining gas zeroed, partially returned, or fully returned?
4. Can a transaction repeat many invalid precompile calls with only CALL overhead?
5. Does the final report/candidate index preserve invalid selectors separately from valid selectors?

Severity guidance:
- Medium if invalid or malformed calls can repeatedly consume meaningful client/precompile resources at zero precompile gas or cause gas-estimation/revert-accounting mismatch.
- Low if only trivial selector parsing is free and no material resource or accounting impact is shown.
- Informational if invalid selectors are fully charged or fail before meaningful work.
```
