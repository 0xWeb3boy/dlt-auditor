# Code-Shape Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-wide-compare-register-cleanup-32768`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `reserved-register-stale-state`

## Code Shape Summary

- Wide comparison opcodes delegated to ALU helpers that advanced pc but did not reset status registers required by the spec.

## Search Motifs

- WDCM WQCM clear err of
- wideint compare leaves $err
- reserved register cleanup
- stale overflow flag

## Typical Asymmetry

- The vulnerable shape appears when one path carries a security, arithmetic, resource, or lifecycle invariant while a sibling path or generated artifact omits the same enforcement.
- Look for helper APIs, compiler metadata, opcode wrappers, or SDK state caches that are treated as authoritative by downstream code.

## Patch Pattern

- Clear err and of during WDCM/WQCM execution and add reserved-register conformance tests for each opcode.

## False Match Warnings

- No issue if the spec intentionally allows the register to persist.
- No issue if the register value is not observable or branchable after the opcode.
