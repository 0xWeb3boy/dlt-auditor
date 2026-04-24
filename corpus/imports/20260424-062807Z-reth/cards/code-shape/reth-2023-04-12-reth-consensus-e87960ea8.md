# Code-Shape Card

## Metadata

- ID: `reth-2023-04-12-reth-consensus-e87960ea8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `forkchoice-input-validation`

## Code Shape Summary

- Pipeline-entry conditions were enforced inconsistently across two different paths. The restoration path validated only the finalized anchor, while missing-head handling was deferred to a narrower later payload-error path, allowing forkchoice processing to proceed without a single authoritative check that both finalized and head references were locally...

## Search Motifs

- authenticated trie/proof path drops empty-root, revealed-node, or rollback state needed for valid output
- fork-specific consensus rule selected from incomplete boundary inputs or generic validator
- search for `ForkchoiceState` call sites that derive, cache, or validate security-sensitive state
- forkchoice-input-validation fixes that add fail-closed validation before persistence, propagation, or canonicalization

## Typical Asymmetry

- Untrusted or fork-dependent input crosses consensus layer signal -> execution client forkchoice/block state, but fork-state-consistency is incomplete before the code updates or relies on canonical head, payload status, or pipeline scheduling.

## Patch Pattern

- Centralize state-machine guards at the earliest authoritative transition point, using the complete forkchoice input instead of a single field and converting missing local anchors into an explicit syncing/pipeline transition.

## False Match Warnings

- The patch does not prove that prior behavior accepted an invalid chain head or corrupted canonical state
- There is no evidence of attacker-controlled exploitation beyond normal engine/forkchoice inputs
- The commit message and diff do not describe a security incident, exploit, or concrete boundary violation
- A similar patch is lower risk if an earlier mandatory validator already rejects the malformed input before this path.
- Treat as provenance-only if the affected code is test-only, debug-only, or unreachable from peer/RPC/engine/sync inputs.
