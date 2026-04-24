# Code-Shape Card

## Metadata

- ID: `rippled-2025-10-21-rippled-transaction-processing-5ebc29c48`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `reserve-enforcement-bypass`

## Code Shape Summary

- The patch fixes VaultWithdraw handling for non-native self-withdrawals that can create a new holding object. Reusable shape: check for reserve-enforcement was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: transaction-handler missing exact reserve-enforcement check before ledger state, balance/reserve accounting, or transaction authorization outcome
- Motif 2: security-sensitive path reaches ledger state, balance/reserve accounting, or transaction authorization outcome before rejecting malformed, stale, or unauthorized input
- Motif 3: Resolve the effective transaction destination before policy checks, then enforce account existence, destination-tag policy, and reserve requirements at the object-creation boundary.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into ledger state, balance/reserve accounting, or transaction authorization outcome unless the reserve-enforcement gate runs before the state-changing branch.

## Patch Pattern

- Resolve the effective transaction destination before policy checks, then enforce account existence, destination-tag policy, and reserve requirements at the object-creation boundary.

## False Match Warnings

- No reproducer or test contents showing an exploitable reserve bypass are provided.
- No evidence proves direct theft, unauthorized withdrawal, consensus divergence, or node compromise.
