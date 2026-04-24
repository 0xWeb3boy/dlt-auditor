# Code-Shape Card

## Metadata

- ID: `rippled-2017-01-24-rippled-cryptography-b4a16b165`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validator-key-revocation-handling`

## Code Shape Summary

- The patch adds first-class handling for validator master-key revocation manifests and a dedicated [validator_key_revocation] config input. Reusable shape: check for signer-scope-and-domain-binding was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: signature-verification-path missing exact signer-scope-and-domain-binding check before accepted signature, signer identity, manifest, or replay-sensitive object
- Motif 2: security-sensitive path reaches accepted signature, signer identity, manifest, or replay-sensitive object before rejecting malformed, stale, or unauthorized input
- Motif 3: Represent terminal key revocation as a distinct manifest state instead of forcing it through the ordinary key-rotation schema.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into accepted signature, signer identity, manifest, or replay-sensitive object unless the signer-scope-and-domain-binding gate runs before the state-changing branch.

## Patch Pattern

- Represent terminal key revocation as a distinct manifest state instead of forcing it through the ordinary key-rotation schema.

## False Match Warnings

- No evidence shows an attacker could forge a revocation manifest or ordinary manifest.
- No evidence shows prior code accepted unauthorized validations.
