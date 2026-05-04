# Code-Shape Card

## Metadata

- ID: `snarkos-2026-01-27-snarkos-p2p-networking-46322b47a`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `p2p-peer-misbehavior-enforcement`

## Code Shape Summary

- Block response validation returns consensus-version-specific errors, but inbound handlers log/return failure without consistently banning the offending peer.

## Search Motifs

- InsertBlockResponseError logged but no peer ban
- ConsensusVersionMismatch branch returns false only
- ip_ban_peer added around invalid block response error arm

## Typical Asymmetry

- The code has a validation, authentication, sizing, correlation, or peer-enforcement concept nearby, but the specific inbound path either does not call it, ignores its result, signs too little data, or maps failure to a log/return instead of a state-changing rejection.

## Patch Pattern

- Preserve structured validation errors and map selected invalid block-response errors to ip_ban_peer/disconnect in client and BFT ingress paths.

## False Match Warnings

- If peer scoring elsewhere immediately removes the peer, duplicate ban may be unnecessary
- Benign upgrade mismatches may need grace-period policy
- This is enforcement hardening, not proof invalid blocks were accepted
