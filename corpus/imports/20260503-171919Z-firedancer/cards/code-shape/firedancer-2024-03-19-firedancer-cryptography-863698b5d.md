# Code-Shape Card

## Metadata

- ID: `firedancer-2024-03-19-firedancer-cryptography-863698b5d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-liveness-failure`

## Code Shape Summary

- Replay state failed to carry enough skipped-slot tick information into the first leader slot, leaving later completeness checks with stale tick context.

## Search Motifs

- Motif 1: recent tick hashes not persisted across skipped-slot transitions
- Motif 2: leader handoff state derived from partial PoH history
- Motif 3: block completeness check using stale tick counters

## Typical Asymmetry

- External slot history drives local replay state, but the state machine assumes leader transitions start with fully synchronized tick context.

## Patch Pattern

- Persist recent tick hashes across non-leader periods and explicitly register skipped ticks before starting the next leader slot.

## False Match Warnings

- No demonstrated remote exploit path beyond skipped-slot conditions.
- No evidence of transaction forgery, signature bypass, or replay attack.
