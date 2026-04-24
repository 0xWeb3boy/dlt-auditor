# Code-Shape Card

## Metadata

- ID: `rippled-2014-02-18-rippled-cryptography-ae649ec91`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-canonicalization-hardening`

## Code Shape Summary

- The supported finding is limited to ECDSA signature canonicalization hardening. The patch makes canonicality policy explicit in signature verification paths, most clearly in SerializedTransaction::checkSign, where tfFullyCanonicalSig selects ECDSA::strict and otherwise uses... Reusable shape: check for signer-scope-and-domain-binding was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: signature-verification-path missing exact signer-scope-and-domain-binding check before accepted signature, signer identity, manifest, or replay-sensitive object
- Motif 2: security-sensitive path reaches accepted signature, signer identity, manifest, or replay-sensitive object before rejecting malformed, stale, or unauthorized input
- Motif 3: Thread an explicit signature-canonicality parameter through verification APIs and select the required policy at each protocol boundary.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into accepted signature, signer identity, manifest, or replay-sensitive object unless the signer-scope-and-domain-binding gate runs before the state-changing branch.

## Patch Pattern

- Thread an explicit signature-canonicality parameter through verification APIs and select the required policy at each protocol boundary.

## False Match Warnings

- No concrete exploit path is shown.
- No evidence that invalid signatures could previously authorize transactions.
