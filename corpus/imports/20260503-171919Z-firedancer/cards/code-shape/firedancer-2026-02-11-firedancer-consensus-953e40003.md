# Code-Shape Card

## Metadata

- ID: `firedancer-2026-02-11-firedancer-consensus-953e40003`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `missing-bounds-check-buffer-overflow`

## Code Shape Summary

- The copy-back path trusted a post-call data length even though the caller-side serialized buffer length could be stale in shared-data scenarios.

## Search Motifs

- Motif 1: memcpy guarded by serialized_data_len == post_len
- Motif 2: shared data box leaves caller length stale
- Motif 3: nested execution copy-back uses post-call length without destination check

## Typical Asymmetry

- Nested execution can resize data indirectly, but the caller-side buffer metadata still reflects an older length assumption.

## Patch Pattern

- Require destination/source length equality before copy-back and return an execution error instead of writing mismatched data.

## False Match Warnings

- No proof of remote exploitability or attacker-controlled code execution.
- No evidence of privilege bypass or access-control failure.
