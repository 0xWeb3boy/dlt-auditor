# Code-Shape Card

## Metadata

- ID: `rippled-2016-02-03-rippled-cryptography-b55edfa8f`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `validator-manifest-signature-hardening`

## Code Shape Summary

- The patch changes validator manifest signing and verification from an observed single master-key verification path to a dual-signature manifest format involving both validation key material and master key material. Reusable shape: check for signer-scope-and-domain-binding was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: signature-verification-path missing exact signer-scope-and-domain-binding check before accepted signature, signer identity, manifest, or replay-sensitive object
- Motif 2: security-sensitive path reaches accepted signature, signer identity, manifest, or replay-sensitive object before rejecting malformed, stale, or unauthorized input
- Motif 3: Introduce explicit dual-signature verification for distinct key roles in validator manifests.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into accepted signature, signer identity, manifest, or replay-sensitive object unless the signer-scope-and-domain-binding gate runs before the state-changing branch.

## Patch Pattern

- Introduce explicit dual-signature verification for distinct key roles in validator manifests.

## False Match Warnings

- No advisory, CVE, or explicit vulnerability statement is provided.
- No attack path or forged-manifest scenario is shown.
