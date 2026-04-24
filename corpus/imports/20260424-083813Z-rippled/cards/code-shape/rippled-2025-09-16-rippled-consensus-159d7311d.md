# Code-Shape Card

## Metadata

- ID: `rippled-2025-09-16-rippled-consensus-159d7311d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-ordering-hardening`

## Code Shape Summary

- The patch changes CanonicalTXSet::accountKey from a padded AccountID XORed with salt_ to an amendment-gated BLAKE3(account || salt) derivation, and wires the flag from validated consensus rules in RCLConsensus::Adaptor::doAccept. Reusable shape: check for consensus-safety-invariant was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: consensus-message-or-ledger-close-path missing exact consensus-safety-invariant check before ledger close decision, validator set decision, or consensus safety state
- Motif 2: security-sensitive path reaches ledger close decision, validator set decision, or consensus safety state before rejecting malformed, stale, or unauthorized input
- Motif 3: Amendment-gated replacement of a deterministic linear ordering-key derivation with cryptographic hashing, while preserving the existing CanonicalTXSet insertion structure.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into ledger close decision, validator set decision, or consensus safety state unless the consensus-safety-invariant gate runs before the state-changing branch.

## Patch Pattern

- Amendment-gated replacement of a deterministic linear ordering-key derivation with cryptographic hashing, while preserving the existing CanonicalTXSet insertion structure.

## False Match Warnings

- No supplied evidence shows an actual exploit path against the old XOR construction.
- No supplied evidence demonstrates validator disagreement, ledger fork, replay, authorization bypass, or denial of service.
