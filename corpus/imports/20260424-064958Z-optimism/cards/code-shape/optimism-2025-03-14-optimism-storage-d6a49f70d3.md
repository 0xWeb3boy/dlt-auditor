# Code-Shape Card

## Metadata

- ID: `optimism-2025-03-14-optimism-storage-d6a49f70d3`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incomplete-verification-binding`

## Code Shape Summary

- The buggy shape was a state-storage or reset/reorg handling path that allowed data or state to approach stored canonicality, proof-window, or derived-state update before fully enforcing input-validation. The shown code suggests earlier verification was bound to a narrower identifier than the newer checksum-based scheme, so the likely issue was incomplete context binding in verification.

## Search Motifs

- state-storage or reset/reorg handling path reaches stored canonicality, proof-window, or derived-state update with partial validation
- input-validation is enforced in one path but missing in an alternate path

## Typical Asymmetry

- The vulnerable asymmetry is that input-validation was enforced only partially, late, or in one lifecycle branch while another branch could still reach stored canonicality, proof-window, or derived-state update.

## Patch Pattern

- Tighten verification by binding acceptance to more complete context and by making temporal validity checks explicit.

## False Match Warnings

- an earlier boundary already rejects the same malformed field under all reachable modes
- the changed code is test-only, generated-only, logging-only, or pure refactor with no runtime decision change
- the input is not attacker-influenced and cannot be affected by a faulty peer, operator, backend, or sequencer
- downstream consensus/proof verification recomputes the property fail-closed before any state or privilege is committed
