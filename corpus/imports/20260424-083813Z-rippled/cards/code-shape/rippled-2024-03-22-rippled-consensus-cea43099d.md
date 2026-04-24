# Code-Shape Card

## Metadata

- ID: `rippled-2024-03-22-rippled-consensus-cea43099d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-desync-hardening`

## Code Shape Summary

- The patch fixes a consensus timing/desynchronization condition where a peer could declare consensus with no received proposals and close a non-validated ledger. Reusable shape: check for consensus-safety-invariant was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: consensus-message-or-ledger-close-path missing exact consensus-safety-invariant check before ledger close decision, validator set decision, or consensus safety state
- Motif 2: security-sensitive path reaches ledger close decision, validator set decision, or consensus safety state before rejecting malformed, stale, or unauthorized input
- Motif 3: Replace an immediate success condition in consensus with an explicit timing gate for the no-proposal case.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into ledger close decision, validator set decision, or consensus safety state unless the consensus-safety-invariant gate runs before the state-changing branch.

## Patch Pattern

- Replace an immediate success condition in consensus with an explicit timing gate for the no-proposal case.

## False Match Warnings

- No proof that an attacker can deliberately trigger delayed proposal delivery or the timing condition.
- No demonstrated theft, double spend, ledger forgery, or consensus safety break.
