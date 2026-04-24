# Code-Shape Card

## Metadata

- ID: `optimism-2022-09-08-optimism-transaction-processing-1c787aa01d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`

## Code Shape Summary

- The buggy shape was a p2p-message-handler that allowed data or state to approach message acceptance, peer selection, or forkchoice update driven by network input before fully enforcing input-validation. The validator accepted attacker-controlled decoded gossip bytes without first enforcing the minimum structure required by later slicing and without authenticating the payload at the earliest trust boundary.

## Search Motifs

- signature accepted without binding all domain/context fields
- chain ID or protected-state converted through lossy integer or metadata path
- signer recovery occurs before payload identity and replay domain are fixed
- p2p-message-handler reaches message acceptance, peer selection, or forkchoice update driven by network input with partial validation
- input-validation is enforced in one path but missing in an alternate path

## Typical Asymmetry

- The vulnerable asymmetry is that input-validation was enforced only partially, late, or in one lifecycle branch while another branch could still reach message acceptance, peer selection, or forkchoice update driven by network input.

## Patch Pattern

- Add explicit structural bounds checks and perform authentication before deeper parsing of network input.

## False Match Warnings

- an earlier boundary already rejects the same malformed field under all reachable modes
- the changed code is test-only, generated-only, logging-only, or pure refactor with no runtime decision change
- the input is not attacker-influenced and cannot be affected by a faulty peer, operator, backend, or sequencer
- downstream consensus/proof verification recomputes the property fail-closed before any state or privilege is committed
