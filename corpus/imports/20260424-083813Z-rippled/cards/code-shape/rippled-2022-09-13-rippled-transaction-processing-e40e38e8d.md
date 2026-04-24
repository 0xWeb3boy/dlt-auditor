# Code-Shape Card

## Metadata

- ID: `rippled-2022-09-13-rippled-transaction-processing-e40e38e8d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unauthorized-resource-consumption`

## Code Shape Summary

- The patch removes the NFTokenMint tfTrustLine capability through the fixRemoveNFTokenAutoTrustLine amendment. Reusable shape: check for resource-accounting was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: authorization-check-path missing exact resource-accounting check before privileged account action, delegated permission, or role-scoped state change
- Motif 2: security-sensitive path reaches privileged account action, delegated permission, or role-scoped state change before rejecting malformed, stale, or unauthorized input
- Motif 3: Remove or gate a protocol flag that allows future third-party transactions to impose issuer reserve costs without issuer consent.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into privileged account action, delegated permission, or role-scoped state change unless the resource-accounting gate runs before the state-changing branch.

## Patch Pattern

- Remove or gate a protocol flag that allows future third-party transactions to impose issuer reserve costs without issuer consent.

## False Match Warnings

- The supplied snippets do not show the full final conditional logic in NFTokenMint::preflight.
- The exact exploit transaction sequence is described in comments but not demonstrated in provided tests.
