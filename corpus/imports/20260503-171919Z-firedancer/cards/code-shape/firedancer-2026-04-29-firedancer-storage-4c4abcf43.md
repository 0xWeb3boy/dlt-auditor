# Code-Shape Card

## Metadata

- ID: `firedancer-2026-04-29-firedancer-storage-4c4abcf43`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `http-content-length-input-validation`

## Code Shape Summary

- Restore logic used permissive Content-Length parsing and accepted zero or malformed values as if they were valid snapshot sizes.

## Search Motifs

- Motif 1: strict content-length parser introduced for snapshot restore
- Motif 2: zero content length rejected for snapshot metadata
- Motif 3: invalid HTTP response canceled on malformed size header

## Typical Asymmetry

- The remote endpoint controls HTTP metadata, but restore code treats the header as trustworthy enough to size critical state.

## Patch Pattern

- Use a strict parser, reject zero or malformed values, and abort restore processing before any body handling depends on the size.

## False Match Warnings

- No proof that an unauthenticated or remote attacker can control the snapshot HTTP response source.
- No demonstrated memory corruption, out-of-bounds access, or integer overflow from the old parser.
