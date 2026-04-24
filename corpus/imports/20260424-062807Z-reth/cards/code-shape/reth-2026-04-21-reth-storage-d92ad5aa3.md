# Code-Shape Card

## Metadata

- ID: `reth-2026-04-21-reth-storage-d92ad5aa3`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-state-binding`

## Code Shape Summary

- Overlay resolution, revert selection, and cache lookup were not consistently tied to the same fork identity. The pre-patch code mixed optional anchor state with block-number-based decisions, which is weaker than explicit hash-based binding when different branches can share the same height.

## Search Motifs

- block-number or optional-anchor checks used where hash identity is required
- improper-state-binding fixes that add fail-closed validation before persistence, propagation, or canonicalization

## Typical Asymmetry

- Untrusted or fork-dependent input crosses forkchoice or sidechain state -> persistent storage provider, but state-coordinate-consistency is incomplete before the code updates or relies on canonical state view, fork ancestry, or persisted trie updates.

## Patch Pattern

- Replace implicit or number-based state selection with explicit hash-threading and hash-based identity checks in overlay resolution, revert calculation, and cache keying.

## False Match Warnings

- No reproducer, advisory, or test demonstrates attacker-triggerable impact
- No patch evidence shows invalid block acceptance, consensus split, or proof forgery
- The touched lazy_overlay.rs file is not shown line-by-line, so its exact security effect is not proven
- A similar patch is lower risk if an earlier mandatory validator already rejects the malformed input before this path.
- Treat as provenance-only if the affected code is test-only, debug-only, or unreachable from peer/RPC/engine/sync inputs.
