# Code-Shape Card

## Metadata

- ID: `optimism-2025-04-30-optimism-p2p-networking-4dd9281e5f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `p2p-identity-handling`

## Code Shape Summary

- The buggy shape was a p2p-message-handler that allowed data or state to approach message acceptance, peer selection, or forkchoice update driven by network input before fully enforcing input-validation. The clearest root cause shown by the diff is permissive identity setup: the p2p builder accepted missing identity material and generated a replacement keypair at runtime.

## Search Motifs

- p2p-message-handler reaches message acceptance, peer selection, or forkchoice update driven by network input with partial validation
- input-validation is enforced in one path but missing in an alternate path

## Typical Asymmetry

- The vulnerable asymmetry is that input-validation was enforced only partially, late, or in one lifecycle branch while another branch could still reach message acceptance, peer selection, or forkchoice update driven by network input.

## Patch Pattern

- Replace silent fallback behavior with explicit configuration errors, and add narrow regression coverage for identity derivation.

## False Match Warnings

- an earlier boundary already rejects the same malformed field under all reachable modes
- the changed code is test-only, generated-only, logging-only, or pure refactor with no runtime decision change
- the input is not attacker-influenced and cannot be affected by a faulty peer, operator, backend, or sequencer
- downstream consensus/proof verification recomputes the property fail-closed before any state or privilege is committed
