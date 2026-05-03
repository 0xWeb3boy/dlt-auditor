# Code-Shape Card

## Metadata

- ID: `firedancer-2025-11-21-firedancer-transaction-processing-48feae326`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `out-of-bounds-read`

## Code Shape Summary

- The code passed a parser a length-limited buffer even though the specific API still required one byte beyond the logical payload.

## Search Motifs

- Motif 1: json_str_sz changed to json_str_sz+1
- Motif 2: WITH_NULL buffer variant introduced for parser path
- Motif 3: ParseWithLength API documented to require sentinel byte

## Typical Asymmetry

- The input length looks correct at the logical layer, but the parser contract assumes a physical backing span with one more byte.

## Patch Pattern

- Provide an extra terminator byte or switch to an API whose contract matches the available backing span.

## False Match Warnings

- No crash trace, sanitizer report, PoC, or exploit scenario is provided.
- No evidence that the overread crosses a sensitive boundary or leaks data.
