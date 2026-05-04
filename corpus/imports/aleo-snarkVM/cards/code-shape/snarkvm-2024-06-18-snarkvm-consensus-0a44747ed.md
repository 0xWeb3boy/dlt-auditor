# Code-Shape Card

## Metadata

- ID: `snarkvm-2024-06-18-snarkvm-consensus-0a44747ed`
- Bug family: `staking_registry_and_accountability`
- Bug class: `validator-limit-enforcement`

## Code Shape Summary

- Finalization code checked the first transition input for a validator address even though the bonded address was carried in the transition Future output.

## Search Motifs

- bond_validator check reads transition.inputs().first()
- committee limit uses data source different from finalization output
- MAX_COMMITTEE_SIZE regression around validator bonding

## Typical Asymmetry

- The code accepted or derived security-sensitive state before proving the boundary property named in the record: `committee-limit-enforcement`.

## Patch Pattern

- Read the validator address from the Future output argument used by finalization and add a maximum-committee-size regression test.

## False Match Warnings

- The first input and Future output are guaranteed equal by a separate enforced constraint.
- The path runs only in tests or offline simulation.
- Committee capacity is rechecked by storage insertion with the authoritative address.
