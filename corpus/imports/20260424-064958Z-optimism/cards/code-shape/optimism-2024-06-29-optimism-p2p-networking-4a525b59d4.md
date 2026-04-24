# Code-Shape Card

## Metadata

- ID: `optimism-2024-06-29-optimism-p2p-networking-4a525b59d4`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `peer-selection-hardening`

## Code Shape Summary

- The buggy shape was a p2p-message-handler that allowed data or state to approach message acceptance, peer selection, or forkchoice update driven by network input before fully enforcing input-validation. No host-driven restriction was enforced in the shown req/resp sync loop for limiting outbound sync requests to static peers.

## Search Motifs

- p2p-message-handler reaches message acceptance, peer selection, or forkchoice update driven by network input with partial validation
- input-validation is enforced in one path but missing in an alternate path

## Typical Asymmetry

- The vulnerable asymmetry is that input-validation was enforced only partially, late, or in one lifecycle branch while another branch could still reach message acceptance, peer selection, or forkchoice update driven by network input.

## Patch Pattern

- Add an optional runtime policy gate in a sensitive path and suppress work for peers outside the allowed set.

## False Match Warnings

- an earlier boundary already rejects the same malformed field under all reachable modes
- the changed code is test-only, generated-only, logging-only, or pure refactor with no runtime decision change
- the input is not attacker-influenced and cannot be affected by a faulty peer, operator, backend, or sequencer
- downstream consensus/proof verification recomputes the property fail-closed before any state or privilege is committed
