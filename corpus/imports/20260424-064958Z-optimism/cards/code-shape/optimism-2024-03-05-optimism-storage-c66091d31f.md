# Code-Shape Card

## Metadata

- ID: `optimism-2024-03-05-optimism-storage-c66091d31f`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `insufficient-domain-separation`

## Code Shape Summary

- The buggy shape was a signature-verification or transaction-decoding path that allowed data or state to approach acceptance of a signature, signer identity, or chain-domain-bound payload before fully enforcing domain-separation. The dispute game appears to have relied on the wrong chain identifier for local preimage context, using shared L1 identity where an L2-specific identity was needed.

## Search Motifs

- signature accepted without binding all domain/context fields
- chain ID or protected-state converted through lossy integer or metadata path
- signer recovery occurs before payload identity and replay domain are fixed
- signature-verification or transaction-decoding path reaches acceptance of a signature, signer identity, or chain-domain-bound payload with partial validation
- domain-separation is enforced in one path but missing in an alternate path

## Typical Asymmetry

- The vulnerable asymmetry is that domain-separation was enforced only partially, late, or in one lifecycle branch while another branch could still reach acceptance of a signature, signer identity, or chain-domain-bound payload.

## Patch Pattern

- Add an explicit domain-specific identifier to contract initialization and state, then use that identifier instead of a broader shared-context identifier.

## False Match Warnings

- an earlier boundary already rejects the same malformed field under all reachable modes
- the changed code is test-only, generated-only, logging-only, or pure refactor with no runtime decision change
- the input is not attacker-influenced and cannot be affected by a faulty peer, operator, backend, or sequencer
- downstream consensus/proof verification recomputes the property fail-closed before any state or privilege is committed
