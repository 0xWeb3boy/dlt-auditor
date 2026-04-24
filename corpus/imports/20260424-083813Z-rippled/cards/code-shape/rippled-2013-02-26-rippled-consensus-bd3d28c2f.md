# Code-Shape Card

## Metadata

- ID: `rippled-2013-02-26-rippled-consensus-bd3d28c2f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-safety`

## Code Shape Summary

- The patch likely fixes a security-relevant consensus correctness bug: a race during consensus startup could let the node begin consensus with the wrong last closed ledger. Reusable shape: check for consensus-safety-invariant was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: consensus-message-or-ledger-close-path missing exact consensus-safety-invariant check before ledger close decision, validator set decision, or consensus safety state
- Motif 2: security-sensitive path reaches ledger close decision, validator set decision, or consensus safety state before rejecting malformed, stale, or unauthorized input
- Motif 3: Centralize timing-sensitive consensus startup behind a shared helper that rechecks network last-closed-ledger state immediately before starting consensus.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into ledger close decision, validator set decision, or consensus safety state unless the consensus-safety-invariant gate runs before the state-changing branch.

## Patch Pattern

- Centralize timing-sensitive consensus startup behind a shared helper that rechecks network last-closed-ledger state immediately before starting consensus.

## False Match Warnings

- No proof that an untrusted peer can reliably trigger the race.
- No tests, traces, or incident notes demonstrating practical exploitation.
