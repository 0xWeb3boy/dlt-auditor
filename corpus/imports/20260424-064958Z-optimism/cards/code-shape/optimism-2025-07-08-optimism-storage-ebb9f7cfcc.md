# Code-Shape Card

## Metadata

- ID: `optimism-2025-07-08-optimism-storage-ebb9f7cfcc`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `derivation-state-consistency`

## Code Shape Summary

- The buggy shape was a state-storage or reset/reorg handling path that allowed data or state to approach stored canonicality, proof-window, or derived-state update before fully enforcing protocol-state-invariant. The evidence points to a state-validation bug in derivation replay/reset handling: non-newer incoming derived pairs were checked against the latest state rather than the stored pair at the same derived height.

## Search Motifs

- state promotion, rewind, or finalization proceeds without parent/canonicality/freshness check
- derivation updates persisted state before all protocol attributes are validated
- fork-specific validation is missing on one post-upgrade branch
- object is internally valid but not checked against requested hash/index/context
- proof or witness hash is computed from the wrong representation or lifecycle point
- external data provider result is consumed before identity binding is verified

## Typical Asymmetry

- The vulnerable asymmetry is that protocol-state-invariant was enforced only partially, late, or in one lifecycle branch while another branch could still reach stored canonicality, proof-window, or derived-state update.

## Patch Pattern

- Correctness hardening: validate replayed/non-newer state against the exact stored record for that height, and make error-path expectations explicit in tests.

## False Match Warnings

- an earlier boundary already rejects the same malformed field under all reachable modes
- the changed code is test-only, generated-only, logging-only, or pure refactor with no runtime decision change
- the input is not attacker-influenced and cannot be affected by a faulty peer, operator, backend, or sequencer
- downstream consensus/proof verification recomputes the property fail-closed before any state or privilege is committed
