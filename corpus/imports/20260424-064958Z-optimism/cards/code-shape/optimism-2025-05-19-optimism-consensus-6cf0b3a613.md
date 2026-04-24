# Code-Shape Card

## Metadata

- ID: `optimism-2025-05-19-optimism-consensus-6cf0b3a613`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unsafe-forkchoice-promotion`

## Code Shape Summary

- The buggy shape was a archive-extraction or file-materialization path that allowed data or state to approach filesystem write outside the intended extraction or artifact directory before fully enforcing path-confinement. Startup logic treated sync progress as sufficient reason to promote forkchoice labels, allowing safe and finalized to be derived from the latest unsafe state rather than from older chain context.

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

- Remove shortcut state promotion in startup recovery and recompute forkchoice from chain context after sync completion.

## False Match Warnings

- an earlier boundary already rejects the same malformed field under all reachable modes
- the changed code is test-only, generated-only, logging-only, or pure refactor with no runtime decision change
- the input is not attacker-influenced and cannot be affected by a faulty peer, operator, backend, or sequencer
- downstream consensus/proof verification recomputes the property fail-closed before any state or privilege is committed
