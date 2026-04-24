# Code-Shape Card

## Metadata

- ID: `rippled-2023-09-11-rippled-p2p-networking-f259cc1ab`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-state-hardening`

## Code Shape Summary

- The patch changes rippled consensus handling to preserve and use peer proposal information across accepted/catch-up states, acquire transaction sets for proposals tied to other ledger sequences, and prune recent peer positions by ledger sequence. Reusable shape: check for consensus-safety-invariant was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: p2p-message-handler missing exact consensus-safety-invariant check before peer session state, fetch scheduling, handshake slots, or local resource accounting
- Motif 2: security-sensitive path reaches peer session state, fetch scheduling, handshake slots, or local resource accounting before rejecting malformed, stale, or unauthorized input
- Motif 3: Retain consensus evidence across phase transitions and ledger-sequence boundaries, acquire missing transaction sets for peer proposals, and prune only consensus state that is no longer needed.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into peer session state, fetch scheduling, handshake slots, or local resource accounting unless the consensus-safety-invariant gate runs before the state-changing branch.

## Patch Pattern

- Retain consensus evidence across phase transitions and ledger-sequence boundaries, acquire missing transaction sets for peer proposals, and prune only consensus state that is no longer needed.

## False Match Warnings

- No evidence shows a malicious peer can reliably trigger the prior behavior.
- No evidence shows forged validations, signature bypass, authentication bypass, or authorization failure.
