# Code-Shape Card

## Metadata

- ID: `reth-2026-01-29-reth-core-logic-bc5e23ddd`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `state-integrity-hardening`

## Code Shape Summary

- The provided evidence supports a correctness fix in parallel sparse trie mutation and rollback handling. The commit message explicitly describes preventing silent trie corruption and correcting restoration to the original subtrie on error. That establishes an integrity/atomicity bug in trie updates, but the supplied material does not establish attacker triggerability or a concrete security exploit path.

## Search Motifs

- Motif 1: TODO
- Motif 2: TODO
- Motif 3: TODO

## Typical Asymmetry

- TODO

## Patch Pattern

- TODO

## False Match Warnings

- TODO
