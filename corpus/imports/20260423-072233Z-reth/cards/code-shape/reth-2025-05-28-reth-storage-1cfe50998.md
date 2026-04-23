# Code-Shape Card

## Metadata

- ID: `reth-2025-05-28-reth-storage-1cfe50998`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `state-integrity-hardening`

## Code Shape Summary

- The persistence path assumed trie updates were present when forked ancestry became canonical. The patch adds ancestor missing-data detection, makes persistence batching fallible, and guards trie-update extraction during canonical removal.

## Search Motifs

- fork ancestry can have missing trie updates
- canonical persistence returns Vec without error path
- remove canonical block blindly takes trie updates

## Typical Asymmetry

- The code has one path that performs the expected validation, accounting, or quality update while a nearby special-case, cache-hit, early-return, or alternate response path omits it.

## Patch Pattern

- Detect missing derived trie data before persistence, recompute or surface errors through a fallible path, and guard handoff of trie updates when removing canonical blocks.

## False Match Warnings

- Missing derived data may only occur in rare internal reorg states.
- A guarded skip is not proof of database corruption.
- Need evidence of persisted bad state before calling this a confirmed vulnerability.
