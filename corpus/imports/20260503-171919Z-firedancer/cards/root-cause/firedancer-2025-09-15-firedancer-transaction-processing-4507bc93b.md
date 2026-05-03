# Root-Cause Card

## Metadata

- ID: `firedancer-2025-09-15-firedancer-transaction-processing-4507bc93b`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `buffer-overflow`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `destination-capacity-validation`

## Violated Invariant

- Invariant: Residual bytes plus a newly received payload must fit the destination buffer before compaction or append.

## Trust Boundary

- Boundary: Peer-controlled network/FEC bytes crossing into a reusable scheduler buffer.

## Attack Surface

- Entrypoint type: buffered network ingest path
- Sensitive sink: memmove/memcpy into a fixed residual buffer

## Impact Pattern

- Primary impact: memory corruption
- Secondary impact: denial of service

## Short Reusable Lesson

- The ingest path compacted residual bytes and appended a new payload without first proving the combined length stayed within the backing buffer.
