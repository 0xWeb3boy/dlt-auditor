# Code-Shape Card

## Metadata

- ID: `rippled-2013-01-19-rippled-transaction-processing-308ca21b9`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `reserve-enforcement-bypass`

## Code Shape Summary

- The grounded substantive fix is in WalletAdd: it changes an account-creation XRP send from a simple balance-versus-amount check to a reserve-aware funding check. Reusable shape: check for reserve-enforcement was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: transaction-handler missing exact reserve-enforcement check before ledger state, balance/reserve accounting, or transaction authorization outcome
- Motif 2: security-sensitive path reaches ledger state, balance/reserve accounting, or transaction authorization outcome before rejecting malformed, stale, or unauthorized input
- Motif 3: Replace a local amount-only funding check with a reserve-aware transaction validity check, and return path-specific unfunded errors for clearer failure attribution.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into ledger state, balance/reserve accounting, or transaction authorization outcome unless the reserve-enforcement gate runs before the state-changing branch.

## Patch Pattern

- Replace a local amount-only funding check with a reserve-aware transaction validity check, and return path-specific unfunded errors for clearer failure attribution.

## False Match Warnings

- No exploit scenario or attacker-controlled sequence is shown.
- No evidence shows theft, double spend, value creation, or consensus divergence.
