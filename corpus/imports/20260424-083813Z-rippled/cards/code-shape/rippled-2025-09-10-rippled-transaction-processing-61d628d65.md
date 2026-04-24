# Code-Shape Card

## Metadata

- ID: `rippled-2025-09-10-rippled-transaction-processing-61d628d65`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`

## Code Shape Summary

- The patch tightens delegated-permission validation under the fixDelegateV1_1 amendment. DelegateSet now rejects invalid, unknown, non-delegatable, or amendment-disabled permission values during preflight, and delegated PaymentMint/PaymentBurn checks reject mismatched SendMax... Reusable shape: check for authorization was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: transaction-handler missing exact authorization check before ledger state, balance/reserve accounting, or transaction authorization outcome
- Motif 2: security-sensitive path reaches ledger state, balance/reserve accounting, or transaction authorization outcome before rejecting malformed, stale, or unauthorized input
- Motif 3: Add amendment-gated, rules-aware permission validation at transaction validation boundaries and enforce same-asset constraints for delegated PaymentMint/PaymentBurn behavior.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into ledger state, balance/reserve accounting, or transaction authorization outcome unless the authorization gate runs before the state-changing branch.

## Patch Pattern

- Add amendment-gated, rules-aware permission validation at transaction validation boundaries and enforce same-asset constraints for delegated PaymentMint/PaymentBurn behavior.

## False Match Warnings

- No exploit transaction or demonstrated attack path is provided.
- No concrete funds theft, consensus failure, or remote compromise impact is shown.
