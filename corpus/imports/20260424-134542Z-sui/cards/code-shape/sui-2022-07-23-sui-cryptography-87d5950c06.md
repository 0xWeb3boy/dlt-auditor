# Code-Shape Card

## Metadata

- ID: `sui-2022-07-23-sui-cryptography-87d5950c06`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `signing-type-registration-hardening`

## Code Shape Summary

- The patch centralizes and seals BcsSignable registration for types that use BCS-based signing helpers. This is security-adjacent hardening of a sensitive signing serialization boundary, but the provided evidence does not establish a concrete vulnerability, exploit path, or prior unsafe behavior beyond distributed trait.

## Search Motifs

- input-validation enforced after parsing but before cryptography state mutation
- cryptography handler accepts externally supplied protocol data
- validation split across helper and sink
- error path treats malformed data as ordinary state

## Typical Asymmetry

- The cryptography sink assumes a property that was only partially established by earlier helper code.

## Patch Pattern

- Replace a broadly implementable public marker trait on a signing helper boundary with a sealed, centralized registration surface.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
