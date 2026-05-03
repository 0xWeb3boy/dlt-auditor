# Code-Shape Card

## Metadata

- ID: `firedancer-2025-12-01-firedancer-core-logic-d94e26080`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `malformed-input-bounds-hardening`

## Code Shape Summary

- A block-oriented parser trusted nested record lengths just enough to advance internal offsets before all backing-buffer checks were complete.

## Search Motifs

- Motif 1: block length compared to buffered size before advancing
- Motif 2: option parser adds bounds check before loop
- Motif 3: simple packet block parsing tightened around minimum length

## Typical Asymmetry

- The file provides nested length fields, but the parser advances shared offsets as if each child length were already trustworthy.

## Patch Pattern

- Validate block and option lengths at each nesting level and refuse to advance offsets when any sub-record exceeds the buffered input.

## False Match Warnings

- No concrete exploit path is shown.
- No proof of attacker-controlled production reachability is supplied.
