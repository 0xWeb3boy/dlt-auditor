# Code-Shape Card

## Metadata

- ID: `rippled-2012-05-15-rippled-transaction-processing-9bbbf24f4`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-claim-authority-proof`

## Code Shape Summary

- The patch changes Claim transactions from carrying GeneratorID plus Generator data to carrying Generator, PubKey, and Signature. Reusable shape: check for authorization was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: authorization-check-path missing exact authorization check before privileged account action, delegated permission, or role-scoped state change
- Motif 2: security-sensitive path reaches privileged account action, delegated permission, or role-scoped state change before rejecting malformed, stale, or unauthorized input
- Motif 3: Replace identifier-only authority representation with required cryptographic proof fields, and update transaction construction to generate and serialize those proof fields.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into privileged account action, delegated permission, or role-scoped state change unless the authorization gate runs before the state-changing branch.

## Patch Pattern

- Replace identifier-only authority representation with required cryptographic proof fields, and update transaction construction to generate and serialize those proof fields.

## False Match Warnings

- No validation path showing the signature is verified.
- No rejection behavior for invalid or missing authority proof is shown.
