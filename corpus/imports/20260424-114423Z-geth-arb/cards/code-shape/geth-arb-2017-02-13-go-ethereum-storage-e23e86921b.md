# Code-Shape Card

## Metadata

- ID: `geth-arb-2017-02-13-go-ethereum-storage-e23e86921b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-content-integrity-check`

## Code Shape Summary

- Incoming chunk data could be processed under a claimed key before recomputing and comparing its content hash.

## Search Motifs

- content-addressed key is trusted without hashing payload
- store request inserts data before key/data equality check
- peer supplied object ID is not bound to bytes
- validation exists in one branch but not an alternate execution path
- object is structurally valid but not checked against the requested protocol coordinate
- fork-specific rule is missing from a generic validator

## Typical Asymmetry

- The vulnerable asymmetry is that content-address-integrity was enforced only partially, late, or in one branch while another path could still reach local store/cache insertion and replication.

## Patch Pattern

- Hash incoming content at admission and reject it when the computed digest does not equal the requested key.

## False Match Warnings

- an earlier mandatory check rejects the same malformed field on every reachable path
- the changed code is test-only, logging-only, generated-only, or pure refactor
- a downstream consensus or proof verifier recomputes the property fail-closed before state changes are committed
- the patch only improves diagnostics, naming, generated bindings, or tests without changing runtime acceptance or rejection
- the input is not attacker-influenced in the deployed threat model
