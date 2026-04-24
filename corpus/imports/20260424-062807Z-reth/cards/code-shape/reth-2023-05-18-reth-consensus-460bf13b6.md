# Code-Shape Card

## Metadata

- ID: `reth-2023-05-18-reth-consensus-460bf13b6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-validation`

## Code Shape Summary

- The evidence points to canonicality being determined too narrowly from in-memory blockchain-tree indices. When a block was canonical in persisted storage but not marked canonical in those indices, the system could classify it too weakly until the DB was consulted.

## Search Motifs

- fork-specific consensus rule selected from incomplete boundary inputs or generic validator
- search for `Syncing` call sites that derive, cache, or validate security-sensitive state
- search for `Invalid` call sites that derive, cache, or validate security-sensitive state
- consensus-validation fixes that add fail-closed validation before persistence, propagation, or canonicalization

## Typical Asymmetry

- Untrusted or fork-dependent input crosses consensus layer signal -> execution client forkchoice/block state, but protocol-rule-enforcement is incomplete before the code updates or relies on canonical head, payload status, or pipeline scheduling.

## Patch Pattern

- Consult persisted canonical state when transient indices are insufficient, then update boundary tests to enforce the corrected protocol status.

## False Match Warnings

- No production hunk from the beacon engine decision path is shown beyond test expectation changes
- No proof is provided that an attacker or peer could exploit the old behavior
- No evidence shows an actual consensus split, state corruption, or denial of service caused by the bug
- A similar patch is lower risk if an earlier mandatory validator already rejects the malformed input before this path.
- Treat as provenance-only if the affected code is test-only, debug-only, or unreachable from peer/RPC/engine/sync inputs.
