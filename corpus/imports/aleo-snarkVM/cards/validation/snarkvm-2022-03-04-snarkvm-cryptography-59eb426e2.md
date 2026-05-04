# Validation Card

## Metadata

- ID: `snarkvm-2022-03-04-snarkvm-cryptography-59eb426e2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unchecked-tree-index-capacity`

## What Confirmed The Issue

- Program function indexes now check against `u8::MAX` before inserting a batch.
- Ledger block-hash indexes now check against `u32::MAX` before inserting block hashes.

## What Could Have Invalidated It

- Consensus constants make the index boundary unreachable.
- The error path is only exercised in synthetic tests with no production caller.

## Severity Guidance

- Expected impact band: availability_or_state_integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- The batch size is already capped by consensus before this function.
- The index type is widened or checked arithmetic is used upstream.
