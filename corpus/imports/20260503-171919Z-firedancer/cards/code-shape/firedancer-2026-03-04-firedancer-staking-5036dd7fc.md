# Code-Shape Card

## Metadata

- ID: `firedancer-2026-03-04-firedancer-staking-5036dd7fc`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `bounds-check-hardening`

## Code Shape Summary

- Reward code indexed a fixed result array directly from delegation metadata even when capacity-derived indexes could exceed the expected range.

## Search Motifs

- Motif 1: idx compared against expected stake-account capacity
- Motif 2: fallback local result buffer used for overflow case
- Motif 3: fixed reward array indexed from external delegation metadata

## Typical Asymmetry

- The reward path assumes capacity planning and actual delegation indexes stay aligned, but real state can exceed that expectation.

## Patch Pattern

- Check the delegation index against capacity first, then use a safe fallback path instead of indexing the fixed array directly.

## False Match Warnings

- No supplied evidence proves an externally triggerable exploit path.
- No supplied evidence proves actual memory corruption, crash, or consensus divergence occurred pre-patch.
