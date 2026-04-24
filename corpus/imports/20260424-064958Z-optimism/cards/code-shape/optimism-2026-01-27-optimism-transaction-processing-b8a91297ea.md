# Code-Shape Card

## Metadata

- ID: `optimism-2026-01-27-optimism-transaction-processing-b8a91297ea`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `integer-truncation`

## Code Shape Summary

- The buggy shape was a p2p-message-handler that allowed data or state to approach message acceptance, peer selection, or forkchoice update driven by network input before fully enforcing domain-separation. Use of permissive big.Int to uint64 conversion in chain-ID-related code paths allowed silent truncation.

## Search Motifs

- signature accepted without binding all domain/context fields
- chain ID or protected-state converted through lossy integer or metadata path
- signer recovery occurs before payload identity and replay domain are fixed
- p2p-message-handler reaches message acceptance, peer selection, or forkchoice update driven by network input with partial validation
- domain-separation is enforced in one path but missing in an alternate path

## Typical Asymmetry

- The vulnerable asymmetry is that domain-separation was enforced only partially, late, or in one lifecycle branch while another branch could still reach message acceptance, peer selection, or forkchoice update driven by network input.

## Patch Pattern

- Replace silent narrowing conversions with strict conversion, and where necessary keep arithmetic in full-precision integer form instead of relying on truncated uint64 values.

## False Match Warnings

- an earlier boundary already rejects the same malformed field under all reachable modes
- the changed code is test-only, generated-only, logging-only, or pure refactor with no runtime decision change
- the input is not attacker-influenced and cannot be affected by a faulty peer, operator, backend, or sequencer
- downstream consensus/proof verification recomputes the property fail-closed before any state or privilege is committed
