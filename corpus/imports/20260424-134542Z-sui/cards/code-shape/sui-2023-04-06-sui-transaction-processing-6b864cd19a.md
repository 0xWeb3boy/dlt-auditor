# Code-Shape Card

## Metadata

- ID: `sui-2023-04-06-sui-transaction-processing-6b864cd19a`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incomplete-ownership-validation`

## Code Shape Summary

- The patch fixes an incomplete gas-object ownership check in Sui transaction validation. Previously, only the primary gas object was required to have `Owner::AddressOwner`; additional gas objects in `more_gas_objs` were not checked by the same validation.

## Search Motifs

- authorization enforced after parsing but before transaction-processing state mutation
- transaction-processing handler accepts externally supplied protocol data
- object authority derived from request fields
- privileged mutation reachable before ownership check

## Typical Asymmetry

- The caller controls identifiers or objects that the sink treats as authority unless ownership is checked first.

## Patch Pattern

- Apply the gas-object ownership invariant uniformly to every gas object accepted by transaction validation, then add downstream invariant checks so deletion of immutable objects is detected if it reaches later execution paths.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
- A later mandatory ownership or capability check rejects the request before any state change.
