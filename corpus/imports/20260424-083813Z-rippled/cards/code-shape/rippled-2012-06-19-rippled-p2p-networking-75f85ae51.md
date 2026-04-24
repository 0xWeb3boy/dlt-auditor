# Code-Shape Card

## Metadata

- ID: `rippled-2012-06-19-rippled-p2p-networking-75f85ae51`
- Bug family: `authz_and_role_gates`
- Bug class: `consensus-role-gating`

## Code Shape Summary

- The patch adds explicit mValidating and mProposing state in LedgerConsensus and gates proposal updates, initial proposal publication, and validation creation/relay on those flags. Reusable shape: check for authorization was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: p2p-message-handler missing exact authorization check before peer session state, fetch scheduling, handshake slots, or local resource accounting
- Motif 2: security-sensitive path reaches peer session state, fetch scheduling, handshake slots, or local resource accounting before rejecting malformed, stale, or unauthorized input
- Motif 3: Introduce explicit local role flags and guard authority-bearing consensus actions with those flags.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into peer session state, fetch scheduling, handshake slots, or local resource accounting unless the authorization gate runs before the state-changing branch.

## Patch Pattern

- Introduce explicit local role flags and guard authority-bearing consensus actions with those flags.

## False Match Warnings

- No Arthur bug report details are provided.
- No peer-side acceptance or rejection rules for validations/proposals are shown.
