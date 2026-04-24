# Code-Shape Card

## Metadata

- ID: `rippled-2021-02-19-rippled-p2p-networking-b4699c3b4`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validator-misbehavior-detection-gap`

## Code Shape Summary

- The patch expands Byzantine validation detector coverage from UNL-only validators to all validations received by the server and adds or tightens related validation and manifest checks. Reusable shape: check for input-validation was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: p2p-message-handler missing exact input-validation check before peer session state, fetch scheduling, handshake slots, or local resource accounting
- Motif 2: security-sensitive path reaches peer session state, fetch scheduling, handshake slots, or local resource accounting before rejecting malformed, stale, or unauthorized input
- Motif 3: Broaden detector input coverage and add stricter validation identity and conflict classification checks around received validations.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into peer session state, fetch scheduling, handshake slots, or local resource accounting unless the input-validation gate runs before the state-changing branch.

## Patch Pattern

- Broaden detector input coverage and add stricter validation identity and conflict classification checks around received validations.

## False Match Warnings

- No evidence that prior behavior allowed invalid validations to affect consensus decisions.
- No demonstrated exploit path, remote attacker capability, fund loss, or ledger safety violation.
