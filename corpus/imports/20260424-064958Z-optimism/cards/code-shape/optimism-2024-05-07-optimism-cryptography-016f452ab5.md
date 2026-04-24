# Code-Shape Card

## Metadata

- ID: `optimism-2024-05-07-optimism-cryptography-016f452ab5`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-integrity-verification`

## Code Shape Summary

- The buggy shape was a proof-or-data-verification path that allowed data or state to approach acceptance of cryptographic, blob, preimage, or proof data into derivation/state before fully enforcing integrity-binding. The issue appears to sit at the boundary between crates/derive/src/types/sidecar.rs and crates/derive/src/online/blob_provider.rs.

## Search Motifs

- object is internally valid but not checked against requested hash/index/context
- proof or witness hash is computed from the wrong representation or lifecycle point
- external data provider result is consumed before identity binding is verified
- proof-or-data-verification path reaches acceptance of cryptographic, blob, preimage, or proof data into derivation/state with partial validation
- integrity-binding is enforced in one path but missing in an alternate path

## Typical Asymmetry

- The vulnerable asymmetry is that integrity-binding was enforced only partially, late, or in one lifecycle branch while another branch could still reach acceptance of cryptographic, blob, preimage, or proof data into derivation/state.

## Patch Pattern

- The fix pattern is to tighten the sensitive cryptography control path so the key invariant is enforced before downstream work continues.

## False Match Warnings

- an earlier boundary already rejects the same malformed field under all reachable modes
- the changed code is test-only, generated-only, logging-only, or pure refactor with no runtime decision change
- the input is not attacker-influenced and cannot be affected by a faulty peer, operator, backend, or sequencer
- downstream consensus/proof verification recomputes the property fail-closed before any state or privilege is committed
