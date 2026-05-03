# Code-Shape Card

## Metadata

- ID: `firedancer-2025-09-19-firedancer-transaction-processing-3d4cbe567`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `stack-buffer-overflow`

## Code Shape Summary

- The call site handed a parser a stack-local object rather than a maximum-sized output buffer, even though the parser contract could write more bytes.

## Search Motifs

- Motif 1: FD_TXN_MAX_SZ or max parser output size introduced at call site
- Motif 2: parser writes into typed object replaced with byte array
- Motif 3: caller allocates header struct where parser expects flexible output buffer

## Typical Asymmetry

- The parser contract allows a larger write than the caller’s local stack object, but that mismatch only shows up on specific attacker-shaped inputs.

## Patch Pattern

- Allocate a correctly aligned maximum-size buffer at the call site and parse into that buffer instead of a too-small typed object.

## False Match Warnings

- No fd_txn_parse contract or documentation is provided to prove the exact required output size.
- No malformed transaction proof of concept is provided.
