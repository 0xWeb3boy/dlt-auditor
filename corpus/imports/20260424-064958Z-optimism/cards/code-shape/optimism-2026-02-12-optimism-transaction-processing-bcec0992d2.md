# Code-Shape Card

## Metadata

- ID: `optimism-2026-02-12-optimism-transaction-processing-bcec0992d2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-derivation-completeness-check`

## Code Shape Summary

- The buggy shape was a proof-or-data-verification path that allowed data or state to approach acceptance of cryptographic, blob, preimage, or proof data into derivation/state before fully enforcing protocol-state-invariant. The visible root cause is missing completeness validation after a successful derivation call: success from advance_to_target(...) was treated as sufficient to continue, even though the returned safe_head could still be below the requested disputed block number.

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

- Add a post-derivation completeness check before using the result as a normal transition output, and map incomplete derivation to a dedicated invalid-transition outcome.

## False Match Warnings

- an earlier boundary already rejects the same malformed field under all reachable modes
- the changed code is test-only, generated-only, logging-only, or pure refactor with no runtime decision change
- the input is not attacker-influenced and cannot be affected by a faulty peer, operator, backend, or sequencer
- downstream consensus/proof verification recomputes the property fail-closed before any state or privilege is committed
