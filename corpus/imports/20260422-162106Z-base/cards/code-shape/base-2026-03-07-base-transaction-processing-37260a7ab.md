# Code-Shape Card

## Metadata

- ID: `base-2026-03-07-base-transaction-processing-37260a7ab`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-validation-hardening`

## Code Shape Summary

- Short description of what the buggy code looked like: The grounded root cause is fragmented proof encoding with incomplete explicit validation at the proposer-side serialization boundary. The evidence only shows that length checks were visible locally before, while `v` validation became explicit after the shared encoder change; it does not show how downstream components handled malformed proof data previously.

## Search Motifs

- Motif 1: manual proof or signature byte assembly duplicated across producer and verifier paths
- Motif 2: signature shape or parity is reconstructed after decode instead of validated canonically
- Motif 3: accepted input depends on signer or signature fields that are not bound consistently end to end

## Typical Asymmetry

- What was checked in one path but missing in another: The code checked that signature material existed, but did not keep one canonical encoding and validation rule bound to the later sink on every path.

## Patch Pattern

- What the fix changed structurally: Centralize serialization of sensitive payloads into a shared encoder and make malformed cryptographic inputs fail early with dedicated error types.

## False Match Warnings

- What looks similar but is often not a bug: Supported claim: the patch adds stricter signature-shape validation and centralizes proof encoding.
