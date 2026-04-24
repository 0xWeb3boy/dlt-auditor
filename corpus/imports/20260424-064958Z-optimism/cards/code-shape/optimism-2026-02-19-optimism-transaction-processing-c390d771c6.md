# Code-Shape Card

## Metadata

- ID: `optimism-2026-02-19-optimism-transaction-processing-c390d771c6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion`

## Code Shape Summary

- The buggy shape was a transaction-handler or batch-derivation path that allowed data or state to approach block payload acceptance, execution attributes, or derived state transition before fully enforcing resource-and-failure-isolation. The decompression path did not consistently enforce the protocol's maximum decompressed-size invariant inside the codec operations themselves.

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

- Apply the protocol size limit inside decompression, cap output-buffer growth at that limit, and preserve the bounded prefix instead of rejecting or expanding without bound.

## False Match Warnings

- an earlier boundary already rejects the same malformed field under all reachable modes
- the changed code is test-only, generated-only, logging-only, or pure refactor with no runtime decision change
- the input is not attacker-influenced and cannot be affected by a faulty peer, operator, backend, or sequencer
- downstream consensus/proof verification recomputes the property fail-closed before any state or privilege is committed
