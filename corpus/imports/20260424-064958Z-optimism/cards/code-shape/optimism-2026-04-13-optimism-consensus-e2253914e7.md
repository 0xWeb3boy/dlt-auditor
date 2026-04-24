# Code-Shape Card

## Metadata

- ID: `optimism-2026-04-13-optimism-consensus-e2253914e7`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `untrusted-input-in-protocol-activation-check`

## Code Shape Summary

- The buggy shape was a transaction-handler or batch-derivation path that allowed data or state to approach block payload acceptance, execution attributes, or derived state transition before fully enforcing freshness-and-fail-closed-validation. A hardfork-activation decision in the batch reader trusted batch.timestamp() from decoded batch data instead of the L1 origin timestamp already available in the derivation pipeline.

## Search Motifs

- state promotion, rewind, or finalization proceeds without parent/canonicality/freshness check
- derivation updates persisted state before all protocol attributes are validated
- fork-specific validation is missing on one post-upgrade branch
- transaction-handler or batch-derivation path reaches block payload acceptance, execution attributes, or derived state transition with partial validation
- freshness-and-fail-closed-validation is enforced in one path but missing in an alternate path

## Typical Asymmetry

- The vulnerable asymmetry is that freshness-and-fail-closed-validation was enforced only partially, late, or in one lifecycle branch while another branch could still reach block payload acceptance, execution attributes, or derived state transition.

## Patch Pattern

- Propagate trusted protocol context into lower-level parsing logic and use it for feature-activation checks instead of attacker-influenced payload fields.

## False Match Warnings

- an earlier boundary already rejects the same malformed field under all reachable modes
- the changed code is test-only, generated-only, logging-only, or pure refactor with no runtime decision change
- the input is not attacker-influenced and cannot be affected by a faulty peer, operator, backend, or sequencer
- downstream consensus/proof verification recomputes the property fail-closed before any state or privilege is committed
