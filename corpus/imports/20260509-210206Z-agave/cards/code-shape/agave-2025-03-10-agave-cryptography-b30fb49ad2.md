# Code-Shape Card

## Metadata

- ID: `agave-2025-03-10-agave-cryptography-b30fb49ad2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `panic-on-invalid-transaction`

## Code Shape Summary

- A packet buffering loop deletes invalid entries from an id-indexed transaction container, then falls through to later code that treats the deleted id as present.

## Search Motifs

- remove_by_id followed by expect transaction must exist
- invalid transaction removed without continue
- expired blockhash branch deletes current item then dereferences it
- container deletion and same-loop infallible lookup

## Typical Asymmetry

- The vulnerable shape trusts an earlier, broader, or non-consuming check while a later security-sensitive sink assumes the data, identity, quota, or state was fully validated.
- The fixed shape moves the check to the boundary that owns the sink, consumes/accounting resources at admission, or carries authenticity/state metadata forward explicitly.

## Patch Pattern

- Add immediate continue/return after removing invalid items so later processing cannot dereference removed container entries.

## False Match Warnings

- The lookup after removal is optional and handled without panic.
- The code always continues or returns immediately after deleting the current item.
- The removed item is not attacker-influenced or the path is test-only.
