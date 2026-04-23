# Code-Shape Card

## Metadata

- ID: `nitro-2022-08-28-nitro-cryptography-d70317ed8`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `message-signature-validation-hardening`

## Code Shape Summary

- Short description of what the buggy code looked like: The patch is security-relevant because it changes sequencer feed signature creation, verification gating, and message hashing. However, the provided evidence does not establish an actual vulnerability, exploitable acceptance path, or production configuration in which forged, replayed, or malformed messages could bypass validation.

## Search Motifs

- Motif 1: message hash construction changes without matching verification cleanup
- Motif 2: signing and verification are conditioned on different mode flags
- Motif 3: a dedicated signature verifier is introduced to replace ad hoc checks in message paths

## Typical Asymmetry

- What was checked in one path but missing in another: One path assembled, hashed, or accepted protocol data with ad hoc rules, while the sensitive sink implicitly assumed a single canonical encoding and verification policy.

## Patch Pattern

- What the fix changed structurally: Clarify signature applicability and canonicalize the data being signed, using a dedicated verifier path and strict serialization for hash construction.

## False Match Warnings

- What looks similar but is often not a bug: If the weak mode is explicit development-only behavior, similar code may be intentional hardening rather than a production bug.
