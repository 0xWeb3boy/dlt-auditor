# Code-Shape Card

## Metadata

- ID: `rippled-2012-06-25-rippled-core-logic-93ad67c24`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `hash-domain-separation`

## Code Shape Summary

- The patch is likely a security fix for SHAMap node serialization and hash-prefix handling. Reusable shape: check for signer-scope-and-domain-binding was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: state-transition-or-core-validation-path missing exact signer-scope-and-domain-binding check before ledger invariant, protocol state, or node safety decision
- Motif 2: security-sensitive path reaches ledger invariant, protocol state, or node safety decision before rejecting malformed, stale, or unauthorized input
- Motif 3: Centralize fetched-node reconstruction, require explicit serialization format selection, and reject hash or type mismatches before accepting the node.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into ledger invariant, protocol state, or node safety decision unless the signer-scope-and-domain-binding gate runs before the state-changing branch.

## Patch Pattern

- Centralize fetched-node reconstruction, require explicit serialization format selection, and reject hash or type mismatches before accepting the node.

## False Match Warnings

- No exploit scenario or attacker-controlled input path is shown.
- No advisory, test, or vulnerability description is provided.
