# Code-Shape Card

## Metadata

- ID: `moonbeam-2023-01-10-moonbeam-transaction-processing-4fed3e0d2b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `smart-contract-xcm-execute-restriction`

## Code Shape Summary

- The precompile did not have a small early parser for the first four selector bytes. The patch adds a bounds-checked read_u32_selector and a pre_check hook for execute selectors.

## Search Motifs

- precompile dispatch lacks pre_check for execute selector
- ABI selector parsed only after caller policy would need it
- XCM execute exposed through utility precompile

## Typical Asymmetry

- The accepting path trusted a local or current-state predicate, while the sensitive sink required a stronger global, historical, caller-class, domain, or cumulative invariant.

## Patch Pattern

- Add early selector parsing and pre-dispatch policy checks for restricted XCM execute methods.

## False Match Warnings

- Selector checks are unnecessary if all target functions share the same caller policy
- The execute function may already reject contracts in deeper origin conversion
- Mock/test-only precompile code is not a production issue
