# Code-Shape Card

## Metadata

- ID: `rippled-2026-04-09-rippled-storage-87e951470`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`

## Code Shape Summary

- The patch likely fixes an access-control issue in delegated granular transaction permissions. Reusable shape: check for authorization was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: state-storage-or-ledger-update-path missing exact authorization check before persistent ledger state, object index, cache, or history consistency
- Motif 2: security-sensitive path reaches persistent ledger state, object index, cache, or history consistency before rejecting malformed, stale, or unauthorized input
- Motif 3: Centralize delegate entry lookup and transaction-level permission checks, then pass derived granular permissions into transaction-specific semantic validation.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into persistent ledger state, object index, cache, or history consistency unless the authorization gate runs before the state-changing branch.

## Patch Pattern

- Centralize delegate entry lookup and transaction-level permission checks, then pass derived granular permissions into transaction-specific semantic validation.

## False Match Warnings

- No regression test excerpt demonstrates the pre-patch unauthorized behavior.
- No attacker preconditions or exploit sequence are shown.
