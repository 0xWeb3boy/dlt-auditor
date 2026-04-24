# Code-Shape Card

## Metadata

- ID: `optimism-2026-04-07-optimism-storage-5e7de4c09a`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-integrity-check`

## Code Shape Summary

- The buggy shape was a proof-or-data-verification path that allowed data or state to approach acceptance of cryptographic, blob, preimage, or proof data into derivation/state before fully enforcing integrity-binding. The append-only storage path lacked an explicit chain-continuity check at the write entry point, so out-of-order or mismatched block references were not visibly rejected there in the supplied pre-patch code.

## Search Motifs

- object is internally valid but not checked against requested hash/index/context
- proof or witness hash is computed from the wrong representation or lifecycle point
- external data provider result is consumed before identity binding is verified
- proof-or-data-verification path reaches acceptance of cryptographic, blob, preimage, or proof data into derivation/state with partial validation
- integrity-binding is enforced in one path but missing in an alternate path

## Typical Asymmetry

- The vulnerable asymmetry is that integrity-binding was enforced only partially, late, or in one lifecycle branch while another branch could still reach acceptance of cryptographic, blob, preimage, or proof data into derivation/state.

## Patch Pattern

- Add a pre-mutation invariant check to an append-only storage path so writes are rejected unless they extend the current tip.

## False Match Warnings

- an earlier boundary already rejects the same malformed field under all reachable modes
- the changed code is test-only, generated-only, logging-only, or pure refactor with no runtime decision change
- the input is not attacker-influenced and cannot be affected by a faulty peer, operator, backend, or sequencer
- downstream consensus/proof verification recomputes the property fail-closed before any state or privilege is committed
