# Code-Shape Card

## Metadata

- ID: `optimism-2025-05-19-optimism-consensus-dfafb52630`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-forkchoice-initialization`

## Code Shape Summary

- The buggy shape was a archive-extraction or file-materialization path that allowed data or state to approach filesystem write outside the intended extraction or artifact directory before fully enforcing path-confinement. A startup shortcut treated the current unsafe block as safe/finalized based on sync state rather than deriving those labels from the rollup's chain-context rule.

## Search Motifs

- archive extraction joins paths without containment check
- tar entry names, links, or absolute paths reach filesystem writes
- cleanup/overwrite logic trusts paths from the artifact
- state promotion, rewind, or finalization proceeds without parent/canonicality/freshness check
- derivation updates persisted state before all protocol attributes are validated
- fork-specific validation is missing on one post-upgrade branch

## Typical Asymmetry

- The vulnerable asymmetry is that path-confinement was enforced only partially, late, or in one lifecycle branch while another branch could still reach filesystem write outside the intended extraction or artifact directory.

## Patch Pattern

- Remove blind promotion of sensitive forkchoice state at a startup transition and recompute the startup safe point from protocol-specific chain history before resuming normal processing.

## False Match Warnings

- an earlier boundary already rejects the same malformed field under all reachable modes
- the changed code is test-only, generated-only, logging-only, or pure refactor with no runtime decision change
- the input is not attacker-influenced and cannot be affected by a faulty peer, operator, backend, or sequencer
- downstream consensus/proof verification recomputes the property fail-closed before any state or privilege is committed
