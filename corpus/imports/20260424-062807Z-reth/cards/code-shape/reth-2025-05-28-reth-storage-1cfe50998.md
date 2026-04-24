# Code-Shape Card

## Metadata

- ID: `reth-2025-05-28-reth-storage-1cfe50998`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `state-integrity-hardening`

## Code Shape Summary

- The prior logic appears to have assumed trie updates were already available along forked branches that later participate in canonical persistence, without an explicit ancestor check or a guarded handoff when trie data was missing.

## Search Motifs

- trie proof/update path drops empty-root, revealed-node, or rollback state needed for authenticated output
- state-integrity-hardening fixes that add fail-closed validation before persistence, propagation, or canonicalization

## Typical Asymmetry

- Untrusted or fork-dependent input crosses execution/engine state transition -> persistent storage, but state-coordinate-consistency is incomplete before the code updates or relies on canonical database, trie updates, or state provider output.

## Patch Pattern

- Add explicit missing-data detection and fallible handling at the persistence boundary instead of assuming derived state is always present.

## False Match Warnings

- No proof that an attacker could remotely trigger the bad state through network-delivered blocks
- No demonstration that the prior behavior accepted invalid blocks or caused a real chain split
- No tests, incident report, CVE, or exploit narrative tying the bug to an actual security failure
- A similar patch is lower risk if an earlier mandatory validator already rejects the malformed input before this path.
- Treat as provenance-only if the affected code is test-only, debug-only, or unreachable from peer/RPC/engine/sync inputs.
