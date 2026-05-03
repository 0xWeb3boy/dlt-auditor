# Code-Shape Card

## Metadata

- ID: `firedancer-2025-12-02-firedancer-core-logic-52a2cbfda`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `content-length-integer-overflow`

## Code Shape Summary

- The parser accepted any successfully parsed unsigned value, then later narrowed it to a smaller integer type without an upper-bound check.

## Search Motifs

- Motif 1: strtoul result compared against UINT_MAX after parse
- Motif 2: Content-Length parsed into wider type then narrowed
- Motif 3: header parser only checked for at least one digit before using size

## Typical Asymmetry

- The attacker controls textual length metadata, but downstream code assumes the parsed integer naturally fits the destination width.

## Patch Pattern

- Parse into a wide type, reject values above the destination limit, and only then use the result for allocation or copy sizing.

## False Match Warnings

- No downstream buffer access or read site is shown in the supplied patch evidence.
- No proof of remote exploitability beyond crafted header handling is provided.
