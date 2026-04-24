# Code-Shape Card

## Metadata

- ID: `optimism-2024-10-18-optimism-cryptography-cc4527008e`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `state-validation-hardening`

## Code Shape Summary

- The buggy shape was a proof-or-data-verification path that allowed data or state to approach acceptance of cryptographic, blob, preimage, or proof data into derivation/state before fully enforcing input-validation. The fallback path used the queried local-safe block's derivation record without first proving that the block was the next eligible cross-safe candidate, and the surrounding DB traversal now shows added consistency checks that were previously absent in this path.

## Search Motifs

- object is internally valid but not checked against requested hash/index/context
- proof or witness hash is computed from the wrong representation or lifecycle point
- external data provider result is consumed before identity binding is verified
- proof-or-data-verification path reaches acceptance of cryptographic, blob, preimage, or proof data into derivation/state with partial validation
- input-validation is enforced in one path but missing in an alternate path

## Typical Asymmetry

- The vulnerable asymmetry is that input-validation was enforced only partially, late, or in one lifecycle branch while another branch could still reach acceptance of cryptographic, blob, preimage, or proof data into derivation/state.

## Patch Pattern

- Replace a direct fallback lookup with explicit candidate computation and fail-closed consistency checks.

## False Match Warnings

- an earlier boundary already rejects the same malformed field under all reachable modes
- the changed code is test-only, generated-only, logging-only, or pure refactor with no runtime decision change
- the input is not attacker-influenced and cannot be affected by a faulty peer, operator, backend, or sequencer
- downstream consensus/proof verification recomputes the property fail-closed before any state or privilege is committed
