# Code-Shape Card

## Metadata

- ID: `optimism-2022-09-08-optimism-transaction-processing-a6101c460a`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`

## Code Shape Summary

- The buggy shape was a p2p-message-handler that allowed data or state to approach message acceptance, peer selection, or forkchoice update driven by network input before fully enforcing input-validation. The validator trusted untrusted gossip input too early: it had no explicit minimum decoded-size check before fixed-offset slicing, and it delayed signer authentication until after earlier payload-handling steps.

## Search Motifs

- signature accepted without binding all domain/context fields
- chain ID or protected-state converted through lossy integer or metadata path
- signer recovery occurs before payload identity and replay domain are fixed
- p2p-message-handler reaches message acceptance, peer selection, or forkchoice update driven by network input with partial validation
- input-validation is enforced in one path but missing in an alternate path

## Typical Asymmetry

- The vulnerable asymmetry is that input-validation was enforced only partially, late, or in one lifecycle branch while another branch could still reach message acceptance, peer selection, or forkchoice update driven by network input.

## Patch Pattern

- Add cheap structural validation before fixed-offset parsing, and perform cryptographic authentication before deeper unmarshaling of untrusted network data.

## False Match Warnings

- an earlier boundary already rejects the same malformed field under all reachable modes
- the changed code is test-only, generated-only, logging-only, or pure refactor with no runtime decision change
- the input is not attacker-influenced and cannot be affected by a faulty peer, operator, backend, or sequencer
- downstream consensus/proof verification recomputes the property fail-closed before any state or privilege is committed
