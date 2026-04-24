# Code-Shape Card

## Metadata

- ID: `reth-2026-04-20-reth-storage-d577814eb`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `protocol-validation`

## Code Shape Summary

- The visible root cause is overly coarse validation logic: Amsterdam-specific field handling was modeled with a broad version cutoff and grouped `V5` with older versions, instead of validating against the exact engine method version, message kind, and Amsterdam activation state.

## Search Motifs

- fork-specific consensus rule selected from incomplete boundary inputs or generic validator
- search for `EngineApiMessageVersion::V5` call sites that derive, cache, or validate security-sensitive state
- search for `V5` call sites that derive, cache, or validate security-sensitive state
- protocol-validation fixes that add fail-closed validation before persistence, propagation, or canonicalization

## Typical Asymmetry

- Untrusted or fork-dependent input crosses execution/engine state transition -> persistent storage, but protocol-rule-enforcement is incomplete before the code updates or relies on canonical database, trie updates, or state provider output.

## Patch Pattern

- Replace coarse version-threshold validation with explicit per-endpoint branching and fork-aware checks, then align error reporting with the exact method-version rules.

## False Match Warnings

- No test, trace, advisory, or issue text shows malformed payloads were previously accepted in practice
- No evidence shows chain-state corruption, consensus split, remote exploitation, or attacker-controlled impact
- The provided snippets do not show the full call flow from RPC input to block execution or state commitment
- A similar patch is lower risk if an earlier mandatory validator already rejects the malformed input before this path.
- Treat as provenance-only if the affected code is test-only, debug-only, or unreachable from peer/RPC/engine/sync inputs.
