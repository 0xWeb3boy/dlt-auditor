# Code-Shape Card

## Metadata

- ID: `optimism-2025-05-17-optimism-p2p-networking-8e38834340`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `forkchoice-sync-state`

## Code Shape Summary

- The buggy shape was a p2p-message-handler that allowed data or state to approach message acceptance, peer selection, or forkchoice update driven by network input before fully enforcing protocol-state-invariant. The pre-patch state machine conflated acceptance of a new unsafe payload during sync with established safe/finalized state, and the derivation actor also had a biased-scheduling issue where a closed sync_complete_rx could remain permanently ready.

## Search Motifs

- state promotion, rewind, or finalization proceeds without parent/canonicality/freshness check
- derivation updates persisted state before all protocol attributes are validated
- fork-specific validation is missing on one post-upgrade branch
- p2p-message-handler reaches message acceptance, peer selection, or forkchoice update driven by network input with partial validation
- protocol-state-invariant is enforced in one path but missing in an alternate path

## Typical Asymmetry

- The vulnerable asymmetry is that protocol-state-invariant was enforced only partially, late, or in one lifecycle branch while another branch could still reach message acceptance, peer selection, or forkchoice update driven by network input.

## Patch Pattern

- State-machine correction: distinguish sync phases explicitly, use an explicit zero sentinel for not-yet-established safe/finalized hashes during initial EL sync, and move an always-ready control future to the end of a biased select!.

## False Match Warnings

- an earlier boundary already rejects the same malformed field under all reachable modes
- the changed code is test-only, generated-only, logging-only, or pure refactor with no runtime decision change
- the input is not attacker-influenced and cannot be affected by a faulty peer, operator, backend, or sequencer
- downstream consensus/proof verification recomputes the property fail-closed before any state or privilege is committed
