# Code-Shape Card

## Metadata

- ID: `optimism-2026-02-09-optimism-transaction-processing-68b81dd5bb`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `finalization-boundary-check`

## Code Shape Summary

- The buggy shape was a transaction-handler or batch-derivation path that allowed data or state to approach block payload acceptance, execution attributes, or derived state transition before fully enforcing protocol-state-invariant. computeRewindTargets had access to the current finalized head but did not explicitly reject rewind requests whose target block number was below that finalized boundary before deriving rewind targets.

## Search Motifs

- state promotion, rewind, or finalization proceeds without parent/canonicality/freshness check
- derivation updates persisted state before all protocol attributes are validated
- fork-specific validation is missing on one post-upgrade branch
- transaction-handler or batch-derivation path reaches block payload acceptance, execution attributes, or derived state transition with partial validation
- protocol-state-invariant is enforced in one path but missing in an alternate path

## Typical Asymmetry

- The vulnerable asymmetry is that protocol-state-invariant was enforced only partially, late, or in one lifecycle branch while another branch could still reach block payload acceptance, execution attributes, or derived state transition.

## Patch Pattern

- Add an explicit invariant check at the start of a state-transition helper, return a dedicated error on violation, and add a regression test for the forbidden ordering.

## False Match Warnings

- an earlier boundary already rejects the same malformed field under all reachable modes
- the changed code is test-only, generated-only, logging-only, or pure refactor with no runtime decision change
- the input is not attacker-influenced and cannot be affected by a faulty peer, operator, backend, or sequencer
- downstream consensus/proof verification recomputes the property fail-closed before any state or privilege is committed
