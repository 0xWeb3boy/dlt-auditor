# Root-Cause Card

## Metadata

- ID: `geth-arb-2017-05-12-go-ethereum-transaction-processing-a5f6a1cb7c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-config-compatibility-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `fork-config-compatibility`

## Violated Invariant

- Invariant: Fork configuration changes must be checked for compatibility at every consensus fork boundary before a node accepts a chain config as safe to continue.

## Trust Boundary

- Boundary: operator or persisted chain configuration -> consensus fork selection

## Attack Surface

- Entrypoint type: chain configuration loading or compatibility check
- Sensitive sink: fork rule selection for block validation

## Impact Pattern

- Primary impact: consensus-integrity
- Secondary impact: operator-safety
- Severity guide: medium

## Short Reusable Lesson

- Compatibility checks covered earlier fork blocks but omitted a later fork activation boundary, risking silent rule mismatch after configuration changes. Add the missing fork activation field to the compatibility checker and fail when stored history and new config disagree.
