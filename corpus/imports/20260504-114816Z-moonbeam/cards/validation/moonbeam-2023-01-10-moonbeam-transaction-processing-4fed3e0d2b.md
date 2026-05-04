# Validation Card

## Metadata

- ID: `moonbeam-2023-01-10-moonbeam-transaction-processing-4fed3e0d2b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `smart-contract-xcm-execute-restriction`

## What Confirmed The Issue

- read_u32_selector helper added for safe selector extraction.
- XCM utils precompile gains a pre_check around execute selectors.

## What Could Have Invalidated It

- The restricted selector was not registered or reachable
- Downstream XCM origin conversion already prevented the disallowed caller class

## Severity Guidance

- Expected impact band: cross_domain_execution_policy
- Expected severity band: medium

## False-Positive Cautions

- Selector checks are unnecessary if all target functions share the same caller policy
- The execute function may already reject contracts in deeper origin conversion
