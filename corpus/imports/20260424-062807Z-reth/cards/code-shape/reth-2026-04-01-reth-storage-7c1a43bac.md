# Code-Shape Card

## Metadata

- ID: `reth-2026-04-01-reth-storage-7c1a43bac`
- Bug family: `resource_accounting_and_limits`
- Bug class: `gas-accounting-state-reuse`

## Code Shape Summary

- The cache stored and replayed a composite output object that embedded per-invocation gas state. On cache hits, the code treated that full object as reusable instead of reconstructing caller-specific accounting fields.

## Search Motifs

- limit check accounts for item count but omits byte size, gas state, or remaining range
- gas-accounting-state-reuse fixes that add fail-closed validation before persistence, propagation, or canonicalization

## Typical Asymmetry

- Untrusted or fork-dependent input crosses execution/engine state transition -> persistent storage, but per-call-resource-accounting is incomplete before the code updates or relies on canonical database, trie updates, or state provider output.

## Patch Pattern

- When caching execution results, do not reuse embedded live accounting objects across invocations. Reconstruct invocation-specific state from current inputs and replay only stable cached data.

## False Match Warnings

- No proof that an external attacker can reliably trigger the faulty cache-hit path in a harmful way
- No demonstrated impact such as consensus split, invalid block acceptance/rejection, denial of service, or economic exploit
- No evidence quantifying whether the bug was reachable across trust boundaries or only affected internal correctness
- A similar patch is lower risk if an earlier mandatory validator already rejects the malformed input before this path.
- Treat as provenance-only if the affected code is test-only, debug-only, or unreachable from peer/RPC/engine/sync inputs.
