# Root-Cause Card

## Metadata

- ID: `moonbeam-2023-01-10-moonbeam-transaction-processing-4fed3e0d2b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `smart-contract-xcm-execute-restriction`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `restricted-selector-policy`

## Violated Invariant

- Invariant: A precompile must identify restricted selectors before execution and enforce caller policy for operations that can execute cross-chain messages.

## Trust Boundary

- Boundary: ABI calldata from EVM callers crosses into XCM execution utilities.

## Attack Surface

- Entrypoint type: xcm-precompile-selector
- Sensitive sink: XCM execute operation

## Impact Pattern

- Primary impact: unauthorized-action
- Secondary impact: cross-domain-message-execution, policy-bypass

## Short Reusable Lesson

- The precompile did not have a small early parser for the first four selector bytes. The patch adds a bounds-checked read_u32_selector and a pre_check hook for execute selectors. Add early selector parsing and pre-dispatch policy checks for restricted XCM execute methods.
