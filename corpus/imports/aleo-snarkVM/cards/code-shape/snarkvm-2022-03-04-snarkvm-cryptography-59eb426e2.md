# Code-Shape Card

## Metadata

- ID: `snarkvm-2022-03-04-snarkvm-cryptography-59eb426e2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unchecked-tree-index-capacity`

## Code Shape Summary

- Tree insertion code accepted a current index plus batch length without first checking that the sum stayed within the index type capacity.

## Search Motifs

- current_index + items.len() before tree insertion
- u8 or u32 index used for append-only tree positions
- Merkle path or function index construction lacks capacity precheck

## Typical Asymmetry

- The code accepted or derived security-sensitive state before proving the boundary property named in the record: `index-capacity-bounds`.

## Patch Pattern

- Add explicit capacity checks before mutation and return ordinary errors when a batch would exceed the index range.

## False Match Warnings

- The batch size is already capped by consensus before this function.
- The index type is widened or checked arithmetic is used upstream.
- The path is offline tooling that cannot affect validation or serving.
