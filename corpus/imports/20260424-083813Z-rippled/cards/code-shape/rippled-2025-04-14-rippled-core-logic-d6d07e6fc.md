# Code-Shape Card

## Metadata

- ID: `rippled-2025-04-14-rippled-core-logic-d6d07e6fc`
- Bug family: `authz_and_role_gates`
- Bug class: `authorization-correctness`

## Code Shape Summary

- Likely access-control fix in rippled vault deposit authorization. The patch changes VaultDeposit private-vault handling to read the share MPTokenIssuance, use its DomainID metadata for authorization decisions, and add an apply-time MPTokenAuthorize call for private vault shares. Reusable shape: check for authorization was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: authorization-check-path missing exact authorization check before privileged account action, delegated permission, or role-scoped state change
- Motif 2: security-sensitive path reaches privileged account action, delegated permission, or role-scoped state change before rejecting malformed, stale, or unauthorized input
- Motif 3: Anchor private-vault share authorization to the share MPTokenIssuance ledger entry and explicitly create required MPToken authorization state during deposit application.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into privileged account action, delegated permission, or role-scoped state change unless the authorization gate runs before the state-changing branch.

## Patch Pattern

- Anchor private-vault share authorization to the share MPTokenIssuance ledger entry and explicitly create required MPToken authorization state during deposit application.

## False Match Warnings

- No complete before/after authorization branch is shown.
- No regression test details are provided in the evidence.
