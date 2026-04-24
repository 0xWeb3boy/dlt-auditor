# Code-Shape Card

## Metadata

- ID: `optimism-2024-11-06-optimism-transaction-processing-633aceb2a2`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-metadata-inconsistency`

## Code Shape Summary

- The buggy shape was a signature-verification or transaction-decoding path that allowed data or state to approach acceptance of a signature, signer identity, or chain-domain-bound payload before fully enforcing signer-and-context-binding. The grounded root cause is a split internal representation of legacy signature metadata during decode and reconstruction, compounded by an upstream signature-model/API change.

## Search Motifs

- signature accepted without binding all domain/context fields
- chain ID or protected-state converted through lossy integer or metadata path
- signer recovery occurs before payload identity and replay domain are fixed
- signature-verification or transaction-decoding path reaches acceptance of a signature, signer identity, or chain-domain-bound payload with partial validation
- signer-and-context-binding is enforced in one path but missing in an alternate path

## Typical Asymmetry

- The vulnerable asymmetry is that signer-and-context-binding was enforced only partially, late, or in one lifecycle branch while another branch could still reach acceptance of a signature, signer identity, or chain-domain-bound payload.

## Patch Pattern

- Replace split or reconstructed signature metadata handling with a single canonical decode/rebuild path, and route decoding through explicit validated entrypoints instead of duplicating ad hoc decode logic.

## False Match Warnings

- an earlier boundary already rejects the same malformed field under all reachable modes
- the changed code is test-only, generated-only, logging-only, or pure refactor with no runtime decision change
- the input is not attacker-influenced and cannot be affected by a faulty peer, operator, backend, or sequencer
- downstream consensus/proof verification recomputes the property fail-closed before any state or privilege is committed
