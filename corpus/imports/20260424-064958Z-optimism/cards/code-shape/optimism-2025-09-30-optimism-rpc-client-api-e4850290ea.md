# Code-Shape Card

## Metadata

- ID: `optimism-2025-09-30-optimism-rpc-client-api-e4850290ea`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `race-condition`

## Code Shape Summary

- The buggy shape was a rpc-handler or API validation path that allowed data or state to approach backend forwarding, access-list approval, or service state derived from caller input before fully enforcing input-validation. Shared EngineController state was accessed and mutated from public entrypoints without consistent synchronization, allowing races over fields such as head pointers and FCU-related flags.

## Search Motifs

- state promotion, rewind, or finalization proceeds without parent/canonicality/freshness check
- derivation updates persisted state before all protocol attributes are validated
- fork-specific validation is missing on one post-upgrade branch
- rpc-handler or API validation path reaches backend forwarding, access-list approval, or service state derived from caller input with partial validation
- input-validation is enforced in one path but missing in an alternate path

## Typical Asymmetry

- The vulnerable asymmetry is that input-validation was enforced only partially, late, or in one lifecycle branch while another branch could still reach backend forwarding, access-list approval, or service state derived from caller input.

## Patch Pattern

- Add controller-level mutex protection around stateful entrypoints and route the actual mutation logic through internal helpers that execute while the lock is held.

## False Match Warnings

- an earlier boundary already rejects the same malformed field under all reachable modes
- the changed code is test-only, generated-only, logging-only, or pure refactor with no runtime decision change
- the input is not attacker-influenced and cannot be affected by a faulty peer, operator, backend, or sequencer
- downstream consensus/proof verification recomputes the property fail-closed before any state or privilege is committed
