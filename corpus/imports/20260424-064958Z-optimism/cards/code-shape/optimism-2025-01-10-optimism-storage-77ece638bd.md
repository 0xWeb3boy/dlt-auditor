# Code-Shape Card

## Metadata

- ID: `optimism-2025-01-10-optimism-storage-77ece638bd`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-validation`

## Code Shape Summary

- The buggy shape was a archive-extraction or file-materialization path that allowed data or state to approach filesystem write outside the intended extraction or artifact directory before fully enforcing input-validation. The validation path relied on an incomplete lookup contract: log inclusion was treated as sufficiently identified by block number, log index, and log hash, while timestamp was also part of the surrounding ordering/safety logic.

## Search Motifs

- archive extraction joins paths without containment check
- tar entry names, links, or absolute paths reach filesystem writes
- cleanup/overwrite logic trusts paths from the artifact
- state promotion, rewind, or finalization proceeds without parent/canonicality/freshness check
- derivation updates persisted state before all protocol attributes are validated
- fork-specific validation is missing on one post-upgrade branch

## Typical Asymmetry

- The vulnerable asymmetry is that input-validation was enforced only partially, late, or in one lifecycle branch while another branch could still reach filesystem write outside the intended extraction or artifact directory.

## Patch Pattern

- Strengthen invariant checks by passing all required identity fields through helper APIs and failing closed when reconstructed state does not exactly match the expected sealed-block context.

## False Match Warnings

- an earlier boundary already rejects the same malformed field under all reachable modes
- the changed code is test-only, generated-only, logging-only, or pure refactor with no runtime decision change
- the input is not attacker-influenced and cannot be affected by a faulty peer, operator, backend, or sequencer
- downstream consensus/proof verification recomputes the property fail-closed before any state or privilege is committed
