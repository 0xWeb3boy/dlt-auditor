# Code-Shape Card

## Metadata

- ID: `optimism-2025-04-24-optimism-p2p-networking-e6b7214cb0`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `trusted-signer-resolution`

## Code Shape Summary

- The buggy shape was a p2p-message-handler that allowed data or state to approach message acceptance, peer selection, or forkchoice update driven by network input before fully enforcing signer-and-context-binding. Based on the excerpts, the likely issue was that signer lookup and related runtime metadata handling were not previously factored into an explicit, typed resolution path.

## Search Motifs

- object is internally valid but not checked against requested hash/index/context
- proof or witness hash is computed from the wrong representation or lifecycle point
- external data provider result is consumed before identity binding is verified
- deployment config is applied before required security fields are checked
- chain-specific defaults overwrite or omit privileged role constraints
- unsupported mode combinations are accepted and interpreted later

## Typical Asymmetry

- The vulnerable asymmetry is that signer-and-context-binding was enforced only partially, late, or in one lifecycle branch while another branch could still reach message acceptance, peer selection, or forkchoice update driven by network input.

## Patch Pattern

- Introduce an explicit helper for resolving sensitive runtime-derived configuration and propagate fetch/decode failures as typed errors.

## False Match Warnings

- an earlier boundary already rejects the same malformed field under all reachable modes
- the changed code is test-only, generated-only, logging-only, or pure refactor with no runtime decision change
- the input is not attacker-influenced and cannot be affected by a faulty peer, operator, backend, or sequencer
- downstream consensus/proof verification recomputes the property fail-closed before any state or privilege is committed
