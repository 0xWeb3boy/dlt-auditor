# Code-Shape Card

## Metadata

- ID: `rippled-2025-09-30-rippled-transaction-processing-e1b234cc5`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-object-confusion-hardening`

## Code Shape Summary

- The patch narrows rippled transaction signature-checking helpers so they no longer receive the full PreclaimContext, and it changes multisign branch selection to inspect sigObject rather than ctx.tx. Reusable shape: check for signer-scope-and-domain-binding was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: transaction-handler missing exact signer-scope-and-domain-binding check before ledger state, balance/reserve accounting, or transaction authorization outcome
- Motif 2: security-sensitive path reaches ledger state, balance/reserve accounting, or transaction authorization outcome before rejecting malformed, stale, or unauthorized input
- Motif 3: Apply least-privilege parameter passing at a security-sensitive helper boundary, and ensure authorization branch decisions are derived from the object being validated rather than from a broader context object.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into ledger state, balance/reserve accounting, or transaction authorization outcome unless the signer-scope-and-domain-binding gate runs before the state-changing branch.

## Patch Pattern

- Apply least-privilege parameter passing at a security-sensitive helper boundary, and ensure authorization branch decisions are derived from the object being validated rather than from a broader context object.

## False Match Warnings

- No current caller is shown passing a sigObject different from ctx.tx.
- The commit states the bug is harmless for now.
