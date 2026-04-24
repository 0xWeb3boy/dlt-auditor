# Code-Shape Card

## Metadata

- ID: `rippled-2012-09-01-rippled-cryptography-3bd054748`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-proposal-duplicate-suppression-bypass`

## Code Shape Summary

- The patch fixes duplicate suppression in NetworkOPs::recvPropose. Before the change, the preliminary duplicate key used only proposal sequence, current ledger ID, and public key. Reusable shape: check for consensus-safety-invariant was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: signature-verification-path missing exact consensus-safety-invariant check before accepted signature, signer identity, manifest, or replay-sensitive object
- Motif 2: security-sensitive path reaches accepted signature, signer identity, manifest, or replay-sensitive object before rejecting malformed, stale, or unauthorized input
- Motif 3: Build replay-sensitive or duplicate-suppression keys from the full message identity needed to distinguish valid protocol messages from malformed variants, before allowing a message to suppress later processing.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into accepted signature, signer identity, manifest, or replay-sensitive object unless the consensus-safety-invariant gate runs before the state-changing branch.

## Patch Pattern

- Build replay-sensitive or duplicate-suppression keys from the full message identity needed to distinguish valid protocol messages from malformed variants, before allowing a message to suppress later processing.

## False Match Warnings

- No tests are supplied showing the malformed-proposal scenario.
- No surrounding validity-check code is supplied to prove the exact ordering of duplicate suppression versus validation.
