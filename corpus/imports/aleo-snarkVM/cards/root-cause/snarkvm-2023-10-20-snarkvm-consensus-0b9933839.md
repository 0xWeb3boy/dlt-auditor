# Root-Cause Card

## Metadata

- ID: `snarkvm-2023-10-20-snarkvm-consensus-0b9933839`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `fee-validation-reward-accounting`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `fee-reward-accounting-validation`

## Violated Invariant

- Invariant: Consensus reward ratification must be derived from the same checked transaction fee context that block validation accepts.

## Trust Boundary

- Boundary: confirmed and rejected transaction set -> VM fee and reward finalization

## Attack Surface

- Entrypoint type: block-finalization
- Sensitive sink: priority fee accounting and coinbase reward ratification

## Impact Pattern

- Primary impact: economic accounting integrity
- Secondary impact: consensus validation consistency

## Short Reusable Lesson

- Consensus fee and reward paths should have one authoritative checker with complete transaction context.
