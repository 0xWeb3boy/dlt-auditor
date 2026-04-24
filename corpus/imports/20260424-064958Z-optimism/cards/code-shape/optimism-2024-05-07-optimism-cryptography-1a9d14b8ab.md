# Code-Shape Card

## Metadata

- ID: `optimism-2024-05-07-optimism-cryptography-1a9d14b8ab`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-input-validation`

## Code Shape Summary

- The buggy shape was a proof-or-data-verification path that allowed data or state to approach acceptance of cryptographic, blob, preimage, or proof data into derivation/state before fully enforcing input-validation. Based on the provided snippets, the online blob-fetch path did not enforce full binding between a returned sidecar and the caller's requested IndexedBlobHash before exposing the result to downstream code.

## Search Motifs

- object is internally valid but not checked against requested hash/index/context
- proof or witness hash is computed from the wrong representation or lifecycle point
- external data provider result is consumed before identity binding is verified
- proof-or-data-verification path reaches acceptance of cryptographic, blob, preimage, or proof data into derivation/state with partial validation
- input-validation is enforced in one path but missing in an alternate path

## Typical Asymmetry

- The vulnerable asymmetry is that input-validation was enforced only partially, late, or in one lifecycle branch while another branch could still reach acceptance of cryptographic, blob, preimage, or proof data into derivation/state.

## Patch Pattern

- Move request-binding validation into the provider so externally fetched objects are checked against the caller's expected identity before use.

## False Match Warnings

- an earlier boundary already rejects the same malformed field under all reachable modes
- the changed code is test-only, generated-only, logging-only, or pure refactor with no runtime decision change
- the input is not attacker-influenced and cannot be affected by a faulty peer, operator, backend, or sequencer
- downstream consensus/proof verification recomputes the property fail-closed before any state or privilege is committed
