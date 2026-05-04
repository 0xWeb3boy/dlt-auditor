# Code-Shape Card

## Metadata

- ID: `snarkvm-2023-10-13-snarkvm-transaction-processing-ccfe9d5b6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-state-integrity`

## Code Shape Summary

- Rejected transaction validation accepted stored finalize operations without a direct equality check against freshly computed fee finalization output.

## Search Motifs

- rejected transaction contains finalize operations
- stored fee operations are trusted instead of recomputed
- validation path compares accepted transactions but not rejected ones

## Typical Asymmetry

- The code accepted or derived security-sensitive state before proving the boundary property named in the record: `deterministic-finalization-binding`.

## Patch Pattern

- Carry rejected fee finalize operations explicitly and reject validation when stored operations differ from deterministic recomputation.

## False Match Warnings

- Rejected transaction effects are never included in canonical state.
- A later block-level root comparison already binds the exact same operations.
- The changed code only renames helper methods without altering validation.
