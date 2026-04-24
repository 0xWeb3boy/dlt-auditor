# Code-Shape Card

## Metadata

- ID: `rippled-2017-08-07-rippled-consensus-d90a0647d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-safety`

## Code Shape Summary

- The patch changes rippled validator quorum and UNL sizing rules in a consensus-sensitive path. Reusable shape: check for consensus-safety-invariant was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: consensus-message-or-ledger-close-path missing exact consensus-safety-invariant check before ledger close decision, validator set decision, or consensus safety state
- Motif 2: security-sensitive path reaches ledger close decision, validator set decision, or consensus safety state before rejecting malformed, stale, or unauthorized input
- Motif 3: Add explicit boundary checks and named safety thresholds in consensus quorum calculation, and base fallback behavior on directly observed validator participation.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into ledger close decision, validator set decision, or consensus safety state unless the consensus-safety-invariant gate runs before the state-changing branch.

## Patch Pattern

- Add explicit boundary checks and named safety thresholds in consensus quorum calculation, and base fallback behavior on directly observed validator participation.

## False Match Warnings

- No proof that an attacker can control the quorum configuration.
- No proof that validator lists are attacker-controlled in the affected deployment model.
