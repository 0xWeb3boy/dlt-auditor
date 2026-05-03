# Validation Card

## Metadata

- ID: `firedancer-2026-04-29-firedancer-storage-4c4abcf43`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `http-content-length-input-validation`

## What Confirmed The Issue

- Evidence 1: Commit subject explicitly says the Content-Length parser was hardened.
- Evidence 2: HTTP response Content-Length parsing changed from strtoul to fd_http_parse_content_len with explicit value length.

## What Could Have Invalidated It

- Compensating control 1: No proof that an unauthenticated or remote attacker can control the snapshot HTTP response source.
- Compensating control 2: No demonstrated memory corruption, out-of-bounds access, or integer overflow from the old parser.

## Severity Guidance

- Expected impact band: medium
- Expected severity band: medium

## False-Positive Cautions

- Caution 1: No proof that an unauthenticated or remote attacker can control the snapshot HTTP response source.
- Caution 2: No demonstrated memory corruption, out-of-bounds access, or integer overflow from the old parser.
