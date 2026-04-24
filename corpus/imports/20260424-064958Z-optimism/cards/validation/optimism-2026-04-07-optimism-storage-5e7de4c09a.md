# Validation Card

## Metadata

- ID: `optimism-2026-04-07-optimism-storage-5e7de4c09a`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-integrity-check`

## What Confirmed The Issue

- Adds a parent-hash continuity check before append-only trie writes.
- Fails closed with OpProofsStorageError::OutOfOrder when the new block does not extend the stored tip.
- The changed code is in op-proofs trie storage, an integrity- and replay-sensitive subsystem.
- The other cited fetch_trie_updates hunks are formatting-only and do not weaken the hardening interpretation of the continuity check.

## What Could Have Invalidated It

- No supplied test or regression shows a real pre-patch exploit scenario.
- No evidence shows untrusted or attacker-controlled input can reach this write path.
- No evidence shows invalid proofs, consensus breakage, or user-visible compromise before the change.
- The commit subject fmt + clippy + doc fixes does not independently support a strong vulnerability claim.

## Severity Guidance

- Expected impact band: state-or-proof-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No supplied test or regression shows a real pre-patch exploit scenario.
- No evidence shows untrusted or attacker-controlled input can reach this write path.
- No evidence shows invalid proofs, consensus breakage, or user-visible compromise before the change.
