# Code-Shape Card

## Metadata

- ID: `firedancer-2025-01-10-firedancer-consensus-63a0855e2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `nonce-state-persistence`

## Code Shape Summary

- The runtime validated nonce authority but returned through paths that did not consistently preserve or advance the nonce account state.

## Search Motifs

- Motif 1: authorized nonce account tracked for finalization
- Motif 2: prepared nonce failure state persisted on error
- Motif 3: nonce advance or rollback logic moved into common finalizer

## Typical Asymmetry

- Transactions consume nonce state, but failure-path bookkeeping assumes the success-path persistence logic is sufficient.

## Patch Pattern

- Record the relevant nonce account after validation and finalize that account explicitly on both success and failure paths.

## False Match Warnings

- No concrete attacker workflow or replay transaction is shown.
- No failing test output or regression case is provided in the input.
