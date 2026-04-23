# Code-Shape Card

## Metadata

- ID: `nitro-2022-09-10-nitro-transaction-processing-112522808`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `protocol-handshake-and-signature-validation`

## Code Shape Summary

- Short description of what the buggy code looked like: The supplied evidence shows feed-handshake and test tightening around wrong-chain, missing-metadata, and invalid-signature cases, but it does not establish a concrete vulnerability or show that unsafe messages were previously accepted. This is best treated as unclear security relevance rather than a validated security fix.

## Search Motifs

- Motif 1: handshake code accepts nil or incomplete metadata and leaves later code to notice
- Motif 2: wrong-chain and invalid-signature errors are collapsed into generic failures
- Motif 3: regression tests get added for missing metadata and wrong-chain cases after protocol hardening

## Typical Asymmetry

- What was checked in one path but missing in another: One path assembled, hashed, or accepted protocol data with ad hoc rules, while the sensitive sink implicitly assumed a single canonical encoding and verification policy.

## Patch Pattern

- What the fix changed structurally: Make protocol rejection conditions explicit at the trust boundary and add regression tests that assert exact failure modes.

## False Match Warnings

- What looks similar but is often not a bug: If the weak mode is explicit development-only behavior, similar code may be intentional hardening rather than a production bug.
