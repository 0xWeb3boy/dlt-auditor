# Code-Shape Card

## Metadata

- ID: `reth-2023-01-30-reth-storage-0e24093b0`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `protocol-state-invariant`

## Code Shape Summary

- The account persistence path did not consistently encode and apply the fork-aware empty-account rule. As shown by the added `is_empty()` helper and the new guard in `AccountInfoChangeSet::Created`, empty accounts could be inserted even when post-Spurious-Dragon state clearing should suppress them. The storage-unwind change may help keep rollback exact,...

## Search Motifs

- fork-specific consensus rule selected from incomplete boundary inputs or generic validator
- search for `is_empty()` call sites that derive, cache, or validate security-sensitive state
- search for `AccountInfoChangeSet::Created` call sites that derive, cache, or validate security-sensitive state
- protocol-state-invariant fixes that add fail-closed validation before persistence, propagation, or canonicalization

## Typical Asymmetry

- Untrusted or fork-dependent input crosses execution/engine state transition -> persistent storage, but protocol-rule-enforcement is incomplete before the code updates or relies on canonical database, trie updates, or state provider output.

## Patch Pattern

- Centralize the protocol predicate, thread fork-activation context into the mutation path, reject writes that violate the fork rule, and tighten rollback logic so restored state matches the intended prior view.

## False Match Warnings

- No test, advisory, or commit message explains a concrete security incident or exploit scenario
- No evidence of an observed consensus split, chain rejection, or attacker-triggerable impact is provided
- The storage unwind hunk is not clearly tied to an independently security-relevant flaw from the supplied excerpts
- A similar patch is lower risk if an earlier mandatory validator already rejects the malformed input before this path.
- Treat as provenance-only if the affected code is test-only, debug-only, or unreachable from peer/RPC/engine/sync inputs.
