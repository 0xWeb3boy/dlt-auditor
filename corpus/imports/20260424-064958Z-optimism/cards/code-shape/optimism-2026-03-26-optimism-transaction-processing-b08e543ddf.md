# Code-Shape Card

## Metadata

- ID: `optimism-2026-03-26-optimism-transaction-processing-b08e543ddf`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion`

## Code Shape Summary

- The buggy shape was a transaction-handler or batch-derivation path that allowed data or state to approach block payload acceptance, execution attributes, or derived state transition before fully enforcing resource-and-failure-isolation. The decompression boundary did not encode the size-cap behavior explicitly enough: limit handling in the Brotli path was tied to buffer growth/rejection behavior rather than a clear capped-output rule, and reader state handling around already-decompressed data was implicit.

## Search Motifs

- untrusted bytes decompressed or parsed before enforcing output limits
- validator callback can panic instead of returning a reject/error
- single malformed item aborts an entire batch instead of being isolated
- state promotion, rewind, or finalization proceeds without parent/canonicality/freshness check
- derivation updates persisted state before all protocol attributes are validated
- fork-specific validation is missing on one post-upgrade branch

## Typical Asymmetry

- The vulnerable asymmetry is that resource-and-failure-isolation was enforced only partially, late, or in one lifecycle branch while another branch could still reach block payload acceptance, execution attributes, or derived state transition.

## Patch Pattern

- Make boundary handling explicit: cap decompression output, stop at the configured limit instead of overgrowing or rejecting on the next resize step, and make reader decompression state idempotent.

## False Match Warnings

- an earlier boundary already rejects the same malformed field under all reachable modes
- the changed code is test-only, generated-only, logging-only, or pure refactor with no runtime decision change
- the input is not attacker-influenced and cannot be affected by a faulty peer, operator, backend, or sequencer
- downstream consensus/proof verification recomputes the property fail-closed before any state or privilege is committed
