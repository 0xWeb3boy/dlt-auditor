# Root-Cause Card

## Metadata

- ID: `snarkvm-2024-06-18-snarkvm-consensus-0a44747ed`
- Bug family: `staking_registry_and_accountability`
- Bug class: `validator-limit-enforcement`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `committee-limit-enforcement`

## Violated Invariant

- Invariant: Validator registration limit checks must extract the validator identity from the authoritative state-transition output, not from an unrelated positional input.

## Trust Boundary

- Boundary: bond validator transition -> committee membership finalization

## Attack Surface

- Entrypoint type: staking-registration-path
- Sensitive sink: validator set insertion under maximum committee-size rules

## Impact Pattern

- Primary impact: validator set integrity
- Secondary impact: consensus membership accountability

## Short Reusable Lesson

- Registry invariants should validate the same authoritative identity that the state transition will actually insert.
