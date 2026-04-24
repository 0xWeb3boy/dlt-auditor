# Code-Shape Card

## Metadata

- ID: `rippled-2018-07-27-rippled-consensus-945493d9c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `censorship-detection-observability`

## Code Shape Summary

- The patch is best classified as security hardening for censorship observability in rippled consensus processing. Reusable shape: check for consensus-safety-invariant was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: consensus-message-or-ledger-close-path missing exact consensus-safety-invariant check before ledger close decision, validator set decision, or consensus safety state
- Motif 2: security-sensitive path reaches ledger close decision, validator set decision, or consensus safety state before rejecting malformed, stale, or unauthorized input
- Motif 3: Add monitoring-oriented consensus plumbing: separate transaction application outcomes and maintain detector state across rounds so repeated omission can be warned about.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into ledger close decision, validator set decision, or consensus safety state unless the consensus-safety-invariant gate runs before the state-changing branch.

## Patch Pattern

- Add monitoring-oriented consensus plumbing: separate transaction application outcomes and maintain detector state across rounds so repeated omission can be warned about.

## False Match Warnings

- No excerpt shows a concrete exploit, attack reproduction, or prior vulnerability condition.
- No evidence shows consensus rules were changed to prevent censorship or force transaction inclusion.
