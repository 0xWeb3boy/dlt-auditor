# Code-Shape Card

## Metadata

- ID: `firedancer-2023-09-29-firedancer-access-control-7cbb71919`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `parser-bounds-hardening`

## Code Shape Summary

- The parser relied on protocol-derived size information without consistently threading the actual buffer length through shred decoding and payload accounting.

## Search Motifs

- Motif 1: parser API that omits actual buffer length
- Motif 2: payload size derived from parsed struct instead of validated input span
- Motif 3: minimum-size checks that do not match real packet layout

## Typical Asymmetry

- The attacker controls the packet bytes, but downstream logic treats size/accounting state as already trustworthy.

## Patch Pattern

- Pass the true input length into the parser, distinguish actual from maximum packet sizes, and derive payload slices only after successful decode.

## False Match Warnings

- No concrete vulnerable caller path is shown for short or malformed buffers.
- No before-version implementation is provided showing an actual out-of-bounds read or write.
