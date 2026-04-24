# Code-Shape Card

## Metadata

- ID: `rippled-2026-03-21-rippled-core-logic-311719dae`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `invariant-state-overwrite`

## Code Shape Summary

- Likely security fix in rippled transaction invariant enforcement. The evidence supports a consensus-sensitive invariant bug where boolean violation state could use last-entry overwrite semantics instead of latching any observed violation. Reusable shape: check for input-and-state-invariant-validation was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: state-transition-or-core-validation-path missing exact input-and-state-invariant-validation check before ledger invariant, protocol state, or node safety decision
- Motif 2: security-sensitive path reaches ledger invariant, protocol state, or node safety decision before rejecting malformed, stale, or unauthorized input
- Motif 3: Latch invariant violations with boolean OR across visited entries, while preserving legacy overwrite behavior behind a consensus amendment gate.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into ledger invariant, protocol state, or node safety decision unless the input-and-state-invariant-validation gate runs before the state-changing branch.

## Patch Pattern

- Latch invariant violations with boolean OR across visited entries, while preserving legacy overwrite behavior behind a consensus amendment gate.

## False Match Warnings

- No demonstrated transaction path showing an attacker can create the invalid states.
- No proof that the bug caused consensus divergence, fund loss, authorization bypass, or privilege misuse.
