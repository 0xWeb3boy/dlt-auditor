# Code-Shape Card

## Metadata

- ID: `nitro-2022-03-03-nitro-cryptography-65e9598f0`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `protocol-input-validation`

## Code Shape Summary

- Short description of what the buggy code looked like: The patch changes DAS-backed message handling from using raw bytes after the DAS header as a lookup key to first deserializing a `DataAvailabilityCertificate` and then using `cert.DataHash`.

## Search Motifs

- Motif 1: raw byte slices after a header are reused directly as hashes or keys
- Motif 2: lookup paths consume untyped protocol payload tails instead of parsed structures
- Motif 3: certificate deserialization is added after a long period of ad hoc byte handling

## Typical Asymmetry

- What was checked in one path but missing in another: One path assembled, hashed, or accepted protocol data with ad hoc rules, while the sensitive sink implicitly assumed a single canonical encoding and verification policy.

## Patch Pattern

- What the fix changed structurally: Replace ad hoc byte-slice interpretation with structured decoding at the protocol boundary, then derive lookup inputs from parsed fields.

## False Match Warnings

- What looks similar but is often not a bug: If the weak mode is explicit development-only behavior, similar code may be intentional hardening rather than a production bug.
