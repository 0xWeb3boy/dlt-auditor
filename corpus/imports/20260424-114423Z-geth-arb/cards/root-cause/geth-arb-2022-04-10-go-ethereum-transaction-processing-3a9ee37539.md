# Root-Cause Card

## Metadata

- ID: `geth-arb-2022-04-10-go-ethereum-transaction-processing-3a9ee37539`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `module-root-validation-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `executable-artifact-root-binding`

## Violated Invariant

- Invariant: Executable artifacts selected by alias or root must prove they match the requested canonical module root before validator or staker initialization accepts them.

## Trust Boundary

- Boundary: operator/module-root selection -> machine loader and validator runtime

## Attack Surface

- Entrypoint type: machine loading or validator initialization path
- Sensitive sink: accepted execution machine for validation or staking

## Impact Pattern

- Primary impact: validator-integrity
- Secondary impact: artifact-integrity
- Severity guide: medium

## Short Reusable Lesson

- Machine loading mixed latest-root aliases with explicit module-root requests and needed to verify the loaded machine reported the expected root. Canonicalize aliases first, then compare the loaded artifact root to the requested root before assigning the machine.
