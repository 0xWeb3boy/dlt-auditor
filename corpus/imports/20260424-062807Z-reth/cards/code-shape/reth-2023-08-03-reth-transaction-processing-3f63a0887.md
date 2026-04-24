# Code-Shape Card

## Metadata

- ID: `reth-2023-08-03-reth-transaction-processing-3f63a0887`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `policy-enforcement`

## Code Shape Summary

- The notification API collapsed an added pending transaction into a bare hash too early, which removed propagation-policy metadata before the listener handoff. That made the listener path unable, or at least not obviously able, to distinguish transactions that should be propagated from those that should not.

## Search Motifs

- authenticated trie/proof path drops empty-root, revealed-node, or rollback state needed for valid output
- search for `AddedTransaction` call sites that derive, cache, or validate security-sensitive state
- search for `propagate_allowed` call sites that derive, cache, or validate security-sensitive state
- policy-enforcement fixes that add fail-closed validation before persistence, propagation, or canonicalization

## Typical Asymmetry

- Untrusted or fork-dependent input crosses external transaction source -> mempool policy engine, but peer-policy-gating is incomplete before the code updates or relies on mempool admission, eviction, or propagation decision.

## Patch Pattern

- Preserve security- or policy-relevant metadata across an internal API boundary instead of reducing an object to an identifier before downstream filtering decisions are made.

## False Match Warnings

- The provided excerpt does not show the rest of on_new_pending_transaction, so actual enforcement using propagate_allowed is not visible
- No regression test is shown proving that non-propagatable transactions were previously delivered to ordinary propagation-facing listeners
- The evidence does not prove that these listeners directly drove external peer propagation rather than purely local subscribers
- A similar patch is lower risk if an earlier mandatory validator already rejects the malformed input before this path.
- Treat as provenance-only if the affected code is test-only, debug-only, or unreachable from peer/RPC/engine/sync inputs.
