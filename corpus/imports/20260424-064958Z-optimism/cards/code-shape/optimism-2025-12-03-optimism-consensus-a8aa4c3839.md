# Code-Shape Card

## Metadata

- ID: `optimism-2025-12-03-optimism-consensus-a8aa4c3839`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-input-validation`

## Code Shape Summary

- The buggy shape was a transaction-handler or batch-derivation path that allowed data or state to approach block payload acceptance, execution attributes, or derived state transition before fully enforcing input-validation. Validation and recovery rules were under-enforced in the span-batch path: the code did not explicitly reject an outdated post-safe-head L1 origin in the shown locations, and extraction failures were not normalized into the same flush/retry handling used for invalid span-batch processing.

## Search Motifs

- state promotion, rewind, or finalization proceeds without parent/canonicality/freshness check
- derivation updates persisted state before all protocol attributes are validated
- fork-specific validation is missing on one post-upgrade branch
- transaction-handler or batch-derivation path reaches block payload acceptance, execution attributes, or derived state transition with partial validation
- input-validation is enforced in one path but missing in an alternate path

## Typical Asymmetry

- The vulnerable asymmetry is that input-validation was enforced only partially, late, or in one lifecycle branch while another branch could still reach block payload acceptance, execution attributes, or derived state transition.

## Patch Pattern

- Add explicit invariant checks in validation/derivation paths and convert ambiguous extraction failures into controlled flush-and-retry handling.

## False Match Warnings

- an earlier boundary already rejects the same malformed field under all reachable modes
- the changed code is test-only, generated-only, logging-only, or pure refactor with no runtime decision change
- the input is not attacker-influenced and cannot be affected by a faulty peer, operator, backend, or sequencer
- downstream consensus/proof verification recomputes the property fail-closed before any state or privilege is committed
