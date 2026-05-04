# Code-Shape Card

## Metadata

- ID: `thor-2025-10-24-thor-core-logic-7c638e51`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `unchecked-numeric-conversion`

## Code Shape Summary

- Native staking and housekeeping paths converted big integer amounts into VET units inline and continued without inspecting conversion errors; the fix stores the converted value, checks err, and reverts or returns before mutation.

## Search Motifs

- conversion helper returns value and error but call site ignores error
- ToVET or unit conversion used inline as mutating-method argument
- big.Int amount narrowed before staking/accounting update
- housekeeping reconciliation continues after failed unit conversion

## Typical Asymmetry

- The external or cross-context input is treated as already safe, while the later privileged sink assumes that admission, domain, or cardinality checks already happened upstream.

## Patch Pattern

- Split numeric conversion from state mutation, check the returned error immediately, revert user calls on failure, and stop housekeeping reconciliation before using an invalid converted amount.

## False Match Warnings

- No issue if conversion is total and cannot fail for any reachable input.
- No issue if the unchecked value is used only for display or logging.
- Do not flag call sites that already revert or return on conversion error.
