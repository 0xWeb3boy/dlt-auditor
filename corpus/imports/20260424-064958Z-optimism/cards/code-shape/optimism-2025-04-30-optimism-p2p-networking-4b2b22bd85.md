# Code-Shape Card

## Metadata

- ID: `optimism-2025-04-30-optimism-p2p-networking-4b2b22bd85`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `p2p-identity-configuration-hardening`

## Code Shape Summary

- The buggy shape was a p2p-message-handler that allowed data or state to approach message acceptance, peer selection, or forkchoice update driven by network input before fully enforcing configuration-validation. The evidence shows permissive and potentially inconsistent p2p identity/configuration handling, especially silent fallback key generation, plus related cleanup in event handling and address-policy behavior.

## Search Motifs

- deployment config is applied before required security fields are checked
- chain-specific defaults overwrite or omit privileged role constraints
- unsupported mode combinations are accepted and interpreted later
- p2p-message-handler reaches message acceptance, peer selection, or forkchoice update driven by network input with partial validation
- configuration-validation is enforced in one path but missing in an alternate path

## Typical Asymmetry

- The vulnerable asymmetry is that configuration-validation was enforced only partially, late, or in one lifecycle branch while another branch could still reach message acceptance, peer selection, or forkchoice update driven by network input.

## Patch Pattern

- Replace permissive fallback identity/config behavior with explicit configuration errors, tighten protocol/address-policy handling, and add regression tests for identity derivation.

## False Match Warnings

- an earlier boundary already rejects the same malformed field under all reachable modes
- the changed code is test-only, generated-only, logging-only, or pure refactor with no runtime decision change
- the input is not attacker-influenced and cannot be affected by a faulty peer, operator, backend, or sequencer
- downstream consensus/proof verification recomputes the property fail-closed before any state or privilege is committed
