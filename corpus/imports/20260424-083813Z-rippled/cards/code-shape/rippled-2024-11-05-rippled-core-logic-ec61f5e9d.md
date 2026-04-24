# Code-Shape Card

## Metadata

- ID: `rippled-2024-11-05-rippled-core-logic-ec61f5e9d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-reserve-check`

## Code Shape Summary

- The supported finding is that fixAMMv1_2 adds an amendment-gated reserve check in AMMWithdraw before sending a second withdrawn non-XRP issued asset. Reusable shape: check for reserve-enforcement was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: state-transition-or-core-validation-path missing exact reserve-enforcement check before ledger invariant, protocol state, or node safety decision
- Motif 2: security-sensitive path reaches ledger invariant, protocol state, or node safety decision before rejecting malformed, stale, or unauthorized input
- Motif 3: Add an amendment-gated precondition check before state-changing AMM withdrawal send logic so issued-asset withdrawals that may create trustlines are rejected when reserve requirements are not satisfied.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into ledger invariant, protocol state, or node safety decision unless the reserve-enforcement gate runs before the state-changing branch.

## Patch Pattern

- Add an amendment-gated precondition check before state-changing AMM withdrawal send logic so issued-asset withdrawals that may create trustlines are rejected when reserve requirements are not satisfied.

## False Match Warnings

- No full helper body is provided showing the exact reserve calculation and error behavior.
- No accountSend implementation evidence proves the prior path always missed reserve enforcement.
