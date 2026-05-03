# Validation Card

## Metadata

- ID: `firedancer-2023-09-29-firedancer-access-control-7cbb71919`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `parser-bounds-hardening`

## What Confirmed The Issue

- Evidence 1: fd_shred_parse is explicitly documented as parsing and validating an untrusted shred header.
- Evidence 2: The parser API changes from buf-only to buf plus sz, allowing validation against the actual input length.

## What Could Have Invalidated It

- Compensating control 1: No concrete vulnerable caller path is shown for short or malformed buffers.
- Compensating control 2: No before-version implementation is provided showing an actual out-of-bounds read or write.

## Severity Guidance

- Expected impact band: medium
- Expected severity band: medium

## False-Positive Cautions

- Caution 1: No concrete vulnerable caller path is shown for short or malformed buffers.
- Caution 2: No before-version implementation is provided showing an actual out-of-bounds read or write.
