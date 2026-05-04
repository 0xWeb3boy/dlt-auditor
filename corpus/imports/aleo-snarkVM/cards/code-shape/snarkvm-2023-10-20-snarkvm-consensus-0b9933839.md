# Code-Shape Card

## Metadata

- ID: `snarkvm-2023-10-20-snarkvm-consensus-0b9933839`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `fee-validation-reward-accounting`

## Code Shape Summary

- Fee validation and reward preparation were split between local ledger checks and VM finalization, with incomplete rejected transaction context at some call sites.

## Search Motifs

- ledger check_transaction_basic duplicates VM fee checks
- reward ratification prepared before confirmed priority fees are computed
- rejected transaction context missing from transaction validation

## Typical Asymmetry

- The code accepted or derived security-sensitive state before proving the boundary property named in the record: `fee-reward-accounting-validation`.

## Patch Pattern

- Centralize transaction checking in the VM, pass rejected context, expose rejected objects, and compute priority fees before reward ratification.

## False Match Warnings

- The local and VM checks are provably equivalent and share the same inputs.
- The fee total is recomputed from canonical transaction objects before block acceptance.
- The change only moves code without altering checked data.
