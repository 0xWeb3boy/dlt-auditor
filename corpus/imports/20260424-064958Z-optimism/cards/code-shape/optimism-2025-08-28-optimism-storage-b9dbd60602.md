# Code-Shape Card

## Metadata

- ID: `optimism-2025-08-28-optimism-storage-b9dbd60602`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `state-validation`

## Code Shape Summary

- The buggy shape was a state-storage or reset/reorg handling path that allowed data or state to approach stored canonicality, proof-window, or derived-state update before fully enforcing protocol-state-invariant. The reset path trusted stored derived state as a valid reset point without revalidating that its corresponding L1 source block was still canonical after reorg-sensitive events.

## Search Motifs

- state promotion, rewind, or finalization proceeds without parent/canonicality/freshness check
- derivation updates persisted state before all protocol attributes are validated
- fork-specific validation is missing on one post-upgrade branch
- state-storage or reset/reorg handling path reaches stored canonicality, proof-window, or derived-state update with partial validation
- protocol-state-invariant is enforced in one path but missing in an alternate path

## Typical Asymmetry

- The vulnerable asymmetry is that protocol-state-invariant was enforced only partially, late, or in one lifecycle branch while another branch could still reach stored canonicality, proof-window, or derived-state update.

## Patch Pattern

- Add a fail-closed provenance check before reusing persisted derived state in recovery logic.

## False Match Warnings

- an earlier boundary already rejects the same malformed field under all reachable modes
- the changed code is test-only, generated-only, logging-only, or pure refactor with no runtime decision change
- the input is not attacker-influenced and cannot be affected by a faulty peer, operator, backend, or sequencer
- downstream consensus/proof verification recomputes the property fail-closed before any state or privilege is committed
