# Validation Card

## Metadata

- ID: `snarkvm-2023-10-13-snarkvm-transaction-processing-ccfe9d5b6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-state-integrity`

## What Confirmed The Issue

- Rejected deploy and execute validation now recompute fee finalize operations and compare them to stored data.
- Rejected execute construction now carries computed finalize operations.

## What Could Have Invalidated It

- The stored operations are derived locally and never accepted from block data.
- The block commitment already excludes rejected transaction operations.

## Severity Guidance

- Expected impact band: consensus_state_integrity
- Expected severity band: high_or_medium

## False-Positive Cautions

- Rejected transaction effects are never included in canonical state.
- A later block-level root comparison already binds the exact same operations.
