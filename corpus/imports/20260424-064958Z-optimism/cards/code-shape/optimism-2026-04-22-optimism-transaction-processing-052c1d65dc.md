# Code-Shape Card

## Metadata

- ID: `optimism-2026-04-22-optimism-transaction-processing-052c1d65dc`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-consensus-validation`

## Code Shape Summary

- The buggy shape was a transaction-handler or batch-derivation path that allowed data or state to approach block payload acceptance, execution attributes, or derived state transition before fully enforcing protocol-state-invariant. The root cause was missing fail-closed validation at the SDM post-exec boundary in block execution: the executor did not enforce that post-exec transactions were only valid in the right mode, and it did not enforce that produced refund metadata stayed within a basic gas-usage bound.

## Search Motifs

- state promotion, rewind, or finalization proceeds without parent/canonicality/freshness check
- derivation updates persisted state before all protocol attributes are validated
- fork-specific validation is missing on one post-upgrade branch
- transaction-handler or batch-derivation path reaches block payload acceptance, execution attributes, or derived state transition with partial validation
- protocol-state-invariant is enforced in one path but missing in an alternate path

## Typical Asymmetry

- The vulnerable asymmetry is that protocol-state-invariant was enforced only partially, late, or in one lifecycle branch while another branch could still reach block payload acceptance, execution attributes, or derived state transition.

## Patch Pattern

- Add explicit mode-gating and numeric invariant checks at the point where post-exec transactions and refund metadata are accepted or produced, so malformed inputs fail immediately instead of being silently tolerated.

## False Match Warnings

- an earlier boundary already rejects the same malformed field under all reachable modes
- the changed code is test-only, generated-only, logging-only, or pure refactor with no runtime decision change
- the input is not attacker-influenced and cannot be affected by a faulty peer, operator, backend, or sequencer
- downstream consensus/proof verification recomputes the property fail-closed before any state or privilege is committed
