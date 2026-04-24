# Code-Shape Card

## Metadata

- ID: `reth-2024-02-02-reth-transaction-processing-72b7caa4c`
- Bug family: `resource_accounting_and_limits`
- Bug class: `resource-limit-enforcement`

## Code Shape Summary

- The truncation logic in the parked subpool enforced only the count component of the configured limit. Because removals were computed from `queued - limit.max_txs` and the loop stopped once count overflow was cleared, pools with relatively few but large transactions could remain above the size limit.

## Search Motifs

- limit check accounts for item count but omits byte size, gas state, or remaining range
- resource-limit-enforcement fixes that add fail-closed validation before persistence, propagation, or canonicalization

## Typical Asymmetry

- Untrusted or fork-dependent input crosses external transaction source -> mempool policy engine, but resource-limit-accounting is incomplete before the code updates or relies on mempool admission, eviction, or propagation decision.

## Patch Pattern

- Replace partial limit checks with a single authoritative predicate that covers all tracked resource dimensions, and update tests so mocks faithfully exercise the constrained resource.

## False Match Warnings

- No proof that an external attacker could reliably trigger harmful memory growth or denial of service
- No evidence of an actual crash, panic, consensus failure, or privilege/security-boundary bypass
- No commit message or patch text explicitly describes a vulnerability, exploitability, or security incident
- A similar patch is lower risk if an earlier mandatory validator already rejects the malformed input before this path.
- Treat as provenance-only if the affected code is test-only, debug-only, or unreachable from peer/RPC/engine/sync inputs.
