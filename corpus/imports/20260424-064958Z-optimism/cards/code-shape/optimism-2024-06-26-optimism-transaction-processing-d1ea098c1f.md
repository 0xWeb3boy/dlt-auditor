# Code-Shape Card

## Metadata

- ID: `optimism-2024-06-26-optimism-transaction-processing-d1ea098c1f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incorrect-proof-state-hash`

## Code Shape Summary

- The buggy shape was a proof-or-data-verification path that allowed data or state to approach acceptance of cryptographic, blob, preimage, or proof data into derivation/state before fully enforcing integrity-binding. The evidence points to stage-incorrect and non-canonical state-hash derivation: some callers separately recomputed hashes from encoded witness data, and the shown proof path derived a hash before the execution step instead of taking the post-step hash afterward.

## Search Motifs

- object is internally valid but not checked against requested hash/index/context
- proof or witness hash is computed from the wrong representation or lifecycle point
- external data provider result is consumed before identity binding is verified
- proof-or-data-verification path reaches acceptance of cryptographic, blob, preimage, or proof data into derivation/state with partial validation
- integrity-binding is enforced in one path but missing in an alternate path

## Typical Asymmetry

- The vulnerable asymmetry is that integrity-binding was enforced only partially, late, or in one lifecycle branch while another branch could still reach acceptance of cryptographic, blob, preimage, or proof data into derivation/state.

## Patch Pattern

- Replace separate or timing-sensitive hash recomputation with a single canonical witness-encoding API, and obtain the hash at the correct execution stage.

## False Match Warnings

- an earlier boundary already rejects the same malformed field under all reachable modes
- the changed code is test-only, generated-only, logging-only, or pure refactor with no runtime decision change
- the input is not attacker-influenced and cannot be affected by a faulty peer, operator, backend, or sequencer
- downstream consensus/proof verification recomputes the property fail-closed before any state or privilege is committed
