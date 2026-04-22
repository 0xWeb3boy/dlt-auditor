# Code-Shape Card

## Metadata

- ID: `base-2026-03-07-base-transaction-processing-3e0b436b4`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-validation`

## Code Shape Summary

- Short description of what the buggy code looked like: The visible issue is inconsistent ownership of proof encoding and validation in a sensitive path: proposer-local code performed ad hoc assembly with length checking, while stricter structural validation was not shown there. The patch centralizes that logic in a shared encoder.

## Search Motifs

- Motif 1: manual proof or signature byte assembly duplicated across producer and verifier paths
- Motif 2: signature shape or parity is reconstructed after decode instead of validated canonically
- Motif 3: accepted input depends on signer or signature fields that are not bound consistently end to end

## Typical Asymmetry

- What was checked in one path but missing in another: The code checked that signature material existed, but did not keep one canonical encoding and validation rule bound to the later sink on every path.

## Patch Pattern

- What the fix changed structurally: Centralize cryptographic payload encoding in a shared component and make malformed signature fields fail through explicit validation errors backed by regression tests.

## False Match Warnings

- What looks similar but is often not a bug: Supported claim: the commit hardens signature/proof encoding validation by rejecting invalid ECDSA `v` values in shared code.
