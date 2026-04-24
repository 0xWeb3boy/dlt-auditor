# Code-Shape Card

## Metadata

- ID: `optimism-2025-02-06-optimism-storage-ec85a08ef9`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `state-machine-validation`

## Code Shape Summary

- The buggy shape was a proof-or-data-verification path that allowed data or state to approach acceptance of cryptographic, blob, preimage, or proof data into derivation/state before fully enforcing protocol-state-invariant. The visible changes support a conclusion that the state machine previously handled a timestamp edge case incorrectly or incompletely: a SuperRoot case that should sometimes be treated as a no-op was always processed as a sub-transition, with related ambiguity in how the transition target and.

## Search Motifs

- state promotion, rewind, or finalization proceeds without parent/canonicality/freshness check
- derivation updates persisted state before all protocol attributes are validated
- fork-specific validation is missing on one post-upgrade branch
- object is internally valid but not checked against requested hash/index/context
- proof or witness hash is computed from the wrong representation or lifecycle point
- external data provider result is consumed before identity binding is verified

## Typical Asymmetry

- The vulnerable asymmetry is that protocol-state-invariant was enforced only partially, late, or in one lifecycle branch while another branch could still reach acceptance of cryptographic, blob, preimage, or proof data into derivation/state.

## Patch Pattern

- Add an explicit guard for a state-machine edge case at the dispatch boundary, enforce exact state commitment equality for the no-op case, and align downstream transition inputs and validation with the intended disputed-step semantics.

## False Match Warnings

- an earlier boundary already rejects the same malformed field under all reachable modes
- the changed code is test-only, generated-only, logging-only, or pure refactor with no runtime decision change
- the input is not attacker-influenced and cannot be affected by a faulty peer, operator, backend, or sequencer
- downstream consensus/proof verification recomputes the property fail-closed before any state or privilege is committed
