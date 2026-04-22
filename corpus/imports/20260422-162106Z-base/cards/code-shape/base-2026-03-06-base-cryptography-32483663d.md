# Code-Shape Card

## Metadata

- ID: `base-2026-03-06-base-cryptography-32483663d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`

## Code Shape Summary

- Short description of what the buggy code looked like: The refactor changed `ProofClaim` from a small fixed-shape record into a container holding nested proposal objects and a variable-length vector coming from an untrusted boundary. The supported issue is missing structural validation of that new untrusted shape, especially unbounded collection size and malformed signature blobs.

## Search Motifs

- Motif 1: manual proof or signature byte assembly duplicated across producer and verifier paths
- Motif 2: signature shape or parity is reconstructed after decode instead of validated canonically
- Motif 3: accepted input depends on signer or signature fields that are not bound consistently end to end

## Typical Asymmetry

- What was checked in one path but missing in another: The code checked that signature material existed, but did not keep one canonical encoding and validation rule bound to the later sink on every path.

## Patch Pattern

- What the fix changed structurally: Add explicit boundary validation for deserialized protocol objects: require mandatory collections to be non-empty, cap collection sizes, and enforce fixed-width structural checks on embedded cryptographic byte fields before downstream processing.

## False Match Warnings

- What looks similar but is often not a bug: This supports malformed-input and resource-exhaustion hardening at an untrusted input boundary.
