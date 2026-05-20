# Validation Card

## Metadata

- ID: `nibiru-c4-2024-11-h04-failed-precompile-gas-bypass`
- Bug family: `resource_accounting_and_limits`
- Bug class: `failed-precompile-gas-undercharge`

## What Confirmed The Issue

- Public C4 report section H-04 rated this as High.
- The report or mitigation review links Nibiru remediation PR evidence for this issue class.

## What Could Have Invalidated It

- No issue if gas is consumed in a defer for both success and failure.
- No issue if the failed call performs no meaningful metered work.

## Severity Guidance

- Expected impact band: undercharged failed precompile work
- Expected severity band: high

## False-Positive Cautions

- No issue if gas is consumed in a defer for both success and failure.
- No issue if the failed call performs no meaningful metered work.
- No issue if outer logic always charges the full gas limit on precompile failure.
