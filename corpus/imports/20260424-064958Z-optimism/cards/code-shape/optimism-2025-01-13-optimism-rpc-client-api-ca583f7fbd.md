# Code-Shape Card

## Metadata

- ID: `optimism-2025-01-13-optimism-rpc-client-api-ca583f7fbd`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incorrect-context-binding`

## Code Shape Summary

- The buggy shape was a rpc-handler or API validation path that allowed data or state to approach backend forwarding, access-list approval, or service state derived from caller input before fully enforcing domain-separation. The code relied on ambient context for lookup and verification: default chain selection in prefetcher hint handling, and head.Root() instead of the requested block root in output proof verification.

## Search Motifs

- signature accepted without binding all domain/context fields
- chain ID or protected-state converted through lossy integer or metadata path
- signer recovery occurs before payload identity and replay domain are fixed
- object is internally valid but not checked against requested hash/index/context
- proof or witness hash is computed from the wrong representation or lifecycle point
- external data provider result is consumed before identity binding is verified

## Typical Asymmetry

- The vulnerable asymmetry is that domain-separation was enforced only partially, late, or in one lifecycle branch while another branch could still reach backend forwarding, access-list approval, or service state derived from caller input.

## Patch Pattern

- Replace ambient defaults with explicit context passed through the API boundary, and verify proofs against the exact requested object context.

## False Match Warnings

- an earlier boundary already rejects the same malformed field under all reachable modes
- the changed code is test-only, generated-only, logging-only, or pure refactor with no runtime decision change
- the input is not attacker-influenced and cannot be affected by a faulty peer, operator, backend, or sequencer
- downstream consensus/proof verification recomputes the property fail-closed before any state or privilege is committed
