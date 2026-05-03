# Code-Shape Card

## Metadata

- ID: `firedancer-2023-01-30-firedancer-core-logic-4f66d0180`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `malformed-archive-metadata-parsing`

## Code Shape Summary

- A fixed-width metadata parser trusted whitespace-only or negative numeric fields before proving the parsed values were valid and bounded.

## Search Motifs

- Motif 1: fixed-width header parsed with strtol-style APIs
- Motif 2: negative or whitespace-only size fields accepted
- Motif 3: iterator progress derived from unvalidated archive metadata

## Typical Asymmetry

- The attacker controls textual size metadata, but the parser treats it as trusted iterator control data.

## Patch Pattern

- Constrain numeric parsing to the field width, reject blank or negative sizes, and refuse to advance iterator state on malformed metadata.

## False Match Warnings

- No full parser implementation diff is provided showing exact bounds checks or rejection logic.
- No concrete remote or attacker-controlled input path is established.
