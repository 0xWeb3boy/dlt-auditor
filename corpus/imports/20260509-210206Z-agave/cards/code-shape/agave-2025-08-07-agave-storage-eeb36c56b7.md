# Code-Shape Card

## Metadata

- ID: `agave-2025-08-07-agave-storage-eeb36c56b7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion-hardening`

## Code Shape Summary

- Archive unpacking chooses temporary write-buffer sizes from broad configured output limits, including a forced minimum, instead of the smaller actual archive size.

## Search Motifs

- archive unpack buffer from apparent unpacked size limit
- minimum write buffer allocation for small archive
- allocation ignores input archive metadata length
- min(input_size, limit) missing in decompression path

## Typical Asymmetry

- The vulnerable shape trusts an earlier, broader, or non-consuming check while a later security-sensitive sink assumes the data, identity, quota, or state was fully validated.
- The fixed shape moves the check to the boundary that owns the sink, consumes/accounting resources at admission, or carries authenticity/state metadata forward explicitly.

## Patch Pattern

- Compute unpack buffers from min(input archive size, effective unpack limit), cap them, and adjust downstream buffer handling for smaller bounded writes.

## False Match Warnings

- The archive source is strictly local and trusted.
- A separate hard cap already bounds actual allocation below risky levels.
- The patch only changes throughput tuning without changing allocation bounds.
