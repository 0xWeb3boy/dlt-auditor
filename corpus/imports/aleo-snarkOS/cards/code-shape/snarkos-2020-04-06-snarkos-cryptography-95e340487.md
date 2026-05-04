# Code-Shape Card

## Metadata

- ID: `snarkos-2020-04-06-snarkos-cryptography-95e340487`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `merkle-membership-validation`

## Code Shape Summary

- Ledger/circuit code uses incomplete Merkle parameter objects or leaves non-dummy membership checks inactive, weakening the binding between witness commitments and ledger roots.

## Search Motifs

- P::H::setup used where full MerkleParameters are expected
- commented-out conditionally_check_membership
- Merkle tree constructed without shared parameter object

## Typical Asymmetry

- The code has a validation, authentication, sizing, correlation, or peer-enforcement concept nearby, but the specific inbound path either does not call it, ignores its result, signs too little data, or maps failure to a log/return instead of a state-changing rejection.

## Patch Pattern

- Use full Merkle parameters through setup and tree construction, then activate conditional membership constraints for non-dummy witnesses.

## False Match Warnings

- Dummy/null commitments may intentionally skip membership checks
- A separate enforced membership check in the same circuit can compensate
- Parameter refactors without verifier constraint changes may be non-security
