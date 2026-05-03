# Code-Shape Card

## Metadata

- ID: `firedancer-2025-09-15-firedancer-transaction-processing-4507bc93b`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `buffer-overflow`

## Code Shape Summary

- The ingest path compacted residual bytes and appended a new payload without first proving the combined length stayed within the backing buffer.

## Search Motifs

- Motif 1: residual+incoming size compared to buffer capacity
- Motif 2: source offset asserted before memmove
- Motif 3: append path guarded by explicit destination size check

## Typical Asymmetry

- The attacker controls how much data arrives, but the implementation assumes internal residual state still leaves enough room.

## Patch Pattern

- Assert source offsets, compute the combined residual-plus-incoming length, and reject oversized input before any copy occurs.

## False Match Warnings

- Complete body of the oversized-buffer rejection path is not shown.
- No proof is provided that malformed FEC/residual state is attacker-controllable.
