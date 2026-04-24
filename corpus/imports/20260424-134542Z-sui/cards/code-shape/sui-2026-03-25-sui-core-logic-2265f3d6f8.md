# Code-Shape Card

## Metadata

- ID: `sui-2026-03-25-sui-core-logic-2265f3d6f8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `vm-recursion-bound-hardening`

## Code Shape Summary

- The patch is best classified as VM hardening, not a confirmed vulnerability fix. The evidence supports that recursive `TypeTag` loading and ability computation were changed to use `TypeSize::for_type_traversal()` and helper implementations, consistent with bounding recursive callsites.

## Search Motifs

- resource-accounting enforced after parsing but before core-logic state mutation
- core-logic handler accepts externally supplied protocol data
- validation split across helper and sink
- error path treats malformed data as ordinary state

## Typical Asymmetry

- The core-logic sink assumes a property that was only partially established by earlier helper code.

## Patch Pattern

- Route recursive VM type-processing through explicit traversal state and reject excessive nesting or size through existing VM limit machinery where applicable.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
