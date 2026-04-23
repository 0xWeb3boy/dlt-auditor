# Code-Shape Card

## Metadata

- ID: `nitro-2025-10-01-nitro-cryptography-7bd9fa47b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-payload-integrity-verification`

## Code Shape Summary

- Short description of what the buggy code looked like: The patch replaces a noop payload marker and an always-success verifier with a Keccak-based commitment over the payload plus extras, and enables that verifier on the live DA provider server path.

## Search Motifs

- Motif 1: integrity markers are placeholders or no-op bytes instead of content-derived commitments
- Motif 2: server-side verifiers return success without recomputing payload hashes
- Motif 3: a live provider path enables real commitment verification only in later fixes

## Typical Asymmetry

- What was checked in one path but missing in another: One path assembled, hashed, or accepted protocol data with ad hoc rules, while the sensitive sink implicitly assumed a single canonical encoding and verification policy.

## Patch Pattern

- What the fix changed structurally: Replace placeholder acceptance logic with deterministic verification that recomputes a payload commitment from the received content and protocol metadata before accepting the message.

## False Match Warnings

- What looks similar but is often not a bug: If the weak mode is explicit development-only behavior, similar code may be intentional hardening rather than a production bug.
