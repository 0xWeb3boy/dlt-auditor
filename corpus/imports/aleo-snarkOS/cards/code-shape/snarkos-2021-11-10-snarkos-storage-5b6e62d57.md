# Code-Shape Card

## Metadata

- ID: `snarkos-2021-11-10-snarkos-storage-5b6e62d57`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-fork-choice`

## Code Shape Summary

- Ledger synchronization chooses a peer fork based on greater height even though the intended fork-choice rule depends on aggregate difficulty/weight.

## Search Motifs

- if peer_height > local_height then switch fork
- rollback decision lacks cumulative difficulty comparison
- common ancestor found but only length compared

## Typical Asymmetry

- The code has a validation, authentication, sizing, correlation, or peer-enforcement concept nearby, but the specific inbound path either does not call it, ignores its result, signs too little data, or maps failure to a log/return instead of a state-changing rejection.

## Patch Pattern

- Compute cumulative chain weight from the common ancestor and switch only when the peer fork is heavier under consensus rules.

## False Match Warnings

- Height-based rules may be valid for protocols with fixed uniform block weight
- If the code is only UI progress estimation, not fork choice, it is not security
- A later finality checkpoint may override this path
