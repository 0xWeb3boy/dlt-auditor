# Code-Shape Card

## Metadata

- ID: `optimism-2025-02-06-optimism-storage-6fb1a6d8e0`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `proof-validation-hardening`

## Code Shape Summary

- The buggy shape was a proof-or-data-verification path that allowed data or state to approach acceptance of cryptographic, blob, preimage, or proof data into derivation/state before fully enforcing integrity-binding. The pre-fix logic handled all SuperRoot cases as mutating sub-transitions and used the claimed block number in one transition path, instead of explicitly modeling the boundary case where the disputed step is a no-op tied to the disputed step boundary.

## Search Motifs

- state promotion, rewind, or finalization proceeds without parent/canonicality/freshness check
- derivation updates persisted state before all protocol attributes are validated
- fork-specific validation is missing on one post-upgrade branch
- object is internally valid but not checked against requested hash/index/context
- proof or witness hash is computed from the wrong representation or lifecycle point
- external data provider result is consumed before identity binding is verified

## Typical Asymmetry

- The vulnerable asymmetry is that integrity-binding was enforced only partially, late, or in one lifecycle branch while another branch could still reach acceptance of cryptographic, blob, preimage, or proof data into derivation/state.

## Patch Pattern

- Make the boundary case explicit in the state machine, short-circuit no-op transitions, and align derivation to the disputed step being checked.

## False Match Warnings

- an earlier boundary already rejects the same malformed field under all reachable modes
- the changed code is test-only, generated-only, logging-only, or pure refactor with no runtime decision change
- the input is not attacker-influenced and cannot be affected by a faulty peer, operator, backend, or sequencer
- downstream consensus/proof verification recomputes the property fail-closed before any state or privilege is committed
