# Code-Shape Card

## Metadata

- ID: `rippled-2023-08-18-rippled-consensus-e8a7b2a1f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-state-management`

## Code Shape Summary

- The evidence supports a consensus stability and liveness improvement in rippled, centered on accepted-ledger validation, proposal retention, transaction-set acquisition, and ledger-sequenced proposal tracking. Reusable shape: check for consensus-safety-invariant was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: consensus-message-or-ledger-close-path missing exact consensus-safety-invariant check before ledger close decision, validator set decision, or consensus safety state
- Motif 2: security-sensitive path reaches ledger close decision, validator set decision, or consensus safety state before rejecting malformed, stale, or unauthorized input
- Motif 3: Consensus state-machine robustness: preserve and organize proposal state by ledger sequence, continue processing proposals during accepted-ledger handling, acquire needed transaction sets for future or mismatched proposal positions, and avoid advancing...

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into ledger close decision, validator set decision, or consensus safety state unless the consensus-safety-invariant gate runs before the state-changing branch.

## Patch Pattern

- Consensus state-machine robustness: preserve and organize proposal state by ledger sequence, continue processing proposals during accepted-ledger handling, acquire needed transaction sets for future or mismatched proposal positions, and avoid advancing...

## False Match Warnings

- No demonstrated malicious peer or validator exploit path.
- No proof of fund loss, double spend, ledger corruption, or authorization bypass.
