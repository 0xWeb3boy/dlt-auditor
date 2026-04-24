# Code-Shape Card

## Metadata

- ID: `rippled-2026-04-22-rippled-transaction-processing-2794a7503`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `invariant-check-state-overwrite`

## Code Shape Summary

- The patch fixes invariant detectors that previously overwrote stored boolean violation state for each visited ledger entry. Reusable shape: check for input-and-state-invariant-validation was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: transaction-handler missing exact input-and-state-invariant-validation check before ledger state, balance/reserve accounting, or transaction authorization outcome
- Motif 2: security-sensitive path reaches ledger state, balance/reserve accounting, or transaction authorization outcome before rejecting malformed, stale, or unauthorized input
- Motif 3: Latch invariant violation state across entry traversal by OR-accumulating per-entry predicates instead of overwriting stored detector state.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into ledger state, balance/reserve accounting, or transaction authorization outcome unless the input-and-state-invariant-validation gate runs before the state-changing branch.

## Patch Pattern

- Latch invariant violation state across entry traversal by OR-accumulating per-entry predicates instead of overwriting stored detector state.

## False Match Warnings

- No evidence that an attacker can create the prohibited ledger states.
- No end-to-end exploit path is shown.
