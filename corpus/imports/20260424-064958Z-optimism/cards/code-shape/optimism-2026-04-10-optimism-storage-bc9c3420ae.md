# Code-Shape Card

## Metadata

- ID: `optimism-2026-04-10-optimism-storage-bc9c3420ae`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-state-validation`

## Code Shape Summary

- The buggy shape was a state-storage or reset/reorg handling path that allowed data or state to approach stored canonicality, proof-window, or derived-state update before fully enforcing input-validation. The mutation paths treated missing proof-window state as optional or substituted defaults, and they did not consistently use the stored proof-window boundaries as the authoritative guard for update ordering and reorg replacement.

## Search Motifs

- state-storage or reset/reorg handling path reaches stored canonicality, proof-window, or derived-state update with partial validation
- input-validation is enforced in one path but missing in an alternate path

## Typical Asymmetry

- The vulnerable asymmetry is that input-validation was enforced only partially, late, or in one lifecycle branch while another branch could still reach stored canonicality, proof-window, or derived-state update.

## Patch Pattern

- Replace optional/default-state handling with explicit precondition checks against persisted proof-window metadata.

## False Match Warnings

- an earlier boundary already rejects the same malformed field under all reachable modes
- the changed code is test-only, generated-only, logging-only, or pure refactor with no runtime decision change
- the input is not attacker-influenced and cannot be affected by a faulty peer, operator, backend, or sequencer
- downstream consensus/proof verification recomputes the property fail-closed before any state or privilege is committed
