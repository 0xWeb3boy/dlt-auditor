# Code-Shape Card

## Metadata

- ID: `rippled-2022-05-30-rippled-core-logic-0ecfc7cb1`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `hardening-or-correctness-fix`

## Code Shape Summary

- This is best treated as TLS/SSL context hardening in rippled, not a confirmed vulnerability fix. Reusable shape: check for input-validation was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: state-transition-or-core-validation-path missing exact input-validation check before ledger invariant, protocol state, or node safety decision
- Motif 2: security-sensitive path reaches ledger invariant, protocol state, or node safety decision before rejecting malformed, stale, or unauthorized input
- Motif 3: Harden TLS defaults during SSL context construction, while treating same-file diagnostic changes as support cleanup rather than the security fix itself.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into ledger invariant, protocol state, or node safety decision unless the input-validation gate runs before the state-changing branch.

## Patch Pattern

- Harden TLS defaults during SSL context construction, while treating same-file diagnostic changes as support cleanup rather than the security fix itself.

## False Match Warnings

- Supplied patch excerpts do not show the actual defaultCipherList before/after contents.
- Supplied patch excerpts do not show the certificate-generation changes directly.
