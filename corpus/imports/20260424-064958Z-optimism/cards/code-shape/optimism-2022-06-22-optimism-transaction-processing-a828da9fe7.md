# Code-Shape Card

## Metadata

- ID: `optimism-2022-06-22-optimism-transaction-processing-a828da9fe7`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`

## Code Shape Summary

- The buggy shape was a transaction-handler or batch-derivation path that allowed data or state to approach block payload acceptance, execution attributes, or derived state transition before fully enforcing authorization. Not established by the provided evidence.

## Search Motifs

- role separation checked on one lifecycle path but not initialize/transfer/update
- policy gate depends on caller-supplied context that can be omitted or defaulted
- privileged address or owner field accepted without invariant checks
- state promotion, rewind, or finalization proceeds without parent/canonicality/freshness check
- derivation updates persisted state before all protocol attributes are validated
- fork-specific validation is missing on one post-upgrade branch

## Typical Asymmetry

- The vulnerable asymmetry is that authorization was enforced only partially, late, or in one lifecycle branch while another branch could still reach block payload acceptance, execution attributes, or derived state transition.

## Patch Pattern

- Make role management explicit in the contract interface and deployment path, and add event/test coverage around role changes.

## False Match Warnings

- an earlier boundary already rejects the same malformed field under all reachable modes
- the changed code is test-only, generated-only, logging-only, or pure refactor with no runtime decision change
- the input is not attacker-influenced and cannot be affected by a faulty peer, operator, backend, or sequencer
- downstream consensus/proof verification recomputes the property fail-closed before any state or privilege is committed
