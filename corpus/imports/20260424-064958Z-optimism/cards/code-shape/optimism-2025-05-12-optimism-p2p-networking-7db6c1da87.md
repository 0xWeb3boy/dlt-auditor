# Code-Shape Card

## Metadata

- ID: `optimism-2025-05-12-optimism-p2p-networking-7db6c1da87`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `forkchoice-state-machine-hardening`

## Code Shape Summary

- The buggy shape was a p2p-message-handler that allowed data or state to approach message acceptance, peer selection, or forkchoice update driven by network input before fully enforcing protocol-state-invariant. The code was relying on weaker startup and consumption checks than the updated state-machine contract: forkchoice data could be used without first normalizing some clearly bad startup states, and derivation used a numeric head comparison instead of explicit change-tracking semantics for safe-head updates.

## Search Motifs

- state promotion, rewind, or finalization proceeds without parent/canonicality/freshness check
- derivation updates persisted state before all protocol attributes are validated
- fork-specific validation is missing on one post-upgrade branch
- p2p-message-handler reaches message acceptance, peer selection, or forkchoice update driven by network input with partial validation
- protocol-state-invariant is enforced in one path but missing in an alternate path

## Typical Asymmetry

- The vulnerable asymmetry is that protocol-state-invariant was enforced only partially, late, or in one lifecycle branch while another branch could still reach message acceptance, peer selection, or forkchoice update driven by network input.

## Patch Pattern

- Normalize inconsistent startup state before entering the main traversal path, and replace heuristic duplicate suppression with explicit change-tracking semantics at the derivation boundary.

## False Match Warnings

- an earlier boundary already rejects the same malformed field under all reachable modes
- the changed code is test-only, generated-only, logging-only, or pure refactor with no runtime decision change
- the input is not attacker-influenced and cannot be affected by a faulty peer, operator, backend, or sequencer
- downstream consensus/proof verification recomputes the property fail-closed before any state or privilege is committed
