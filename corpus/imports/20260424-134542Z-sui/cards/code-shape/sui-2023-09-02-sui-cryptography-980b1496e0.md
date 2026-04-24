# Code-Shape Card

## Metadata

- ID: `sui-2023-09-02-sui-cryptography-980b1496e0`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `multisig-input-validation`

## Code Shape Summary

- The patch hardens TypeScript SDK multisig handling by adding validation around `MultiSigPublicKey` construction and partial-signature combination.

## Search Motifs

- signature-verification enforced after parsing but before cryptography state mutation
- cryptography handler accepts externally supplied protocol data
- validation split across helper and sink
- error path treats malformed data as ordinary state

## Typical Asymmetry

- The cryptography sink assumes a property that was only partially established by earlier helper code.

## Patch Pattern

- Add explicit validation at SDK construction and signature-combination boundaries for multisig threshold validity, signer uniqueness, reachable aggregate weight, signer count bounds, and partial signature count bounds.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
