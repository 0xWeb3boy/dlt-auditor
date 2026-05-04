# Root-Cause Card

## Metadata

- ID: `snarkvm-2025-08-24-snarkvm-staking-b51b85078`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `deployment-upgrade-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `upgrade-interface-preservation`

## Violated Invariant

- Invariant: A versioned program upgrade must preserve the interface of existing callable functions unless the active consensus rules explicitly allow a breaking change.

## Trust Boundary

- Boundary: deployment upgrade transaction -> stored program interface

## Attack Surface

- Entrypoint type: deployment-upgrade-validation
- Sensitive sink: acceptance of upgraded program definitions under V10 rules

## Impact Pattern

- Primary impact: upgrade validation consistency
- Secondary impact: state-machine interface preservation

## Short Reusable Lesson

- Consensus-versioned upgrade rules should compare new and existing interface surfaces before accepting a replacement program.
