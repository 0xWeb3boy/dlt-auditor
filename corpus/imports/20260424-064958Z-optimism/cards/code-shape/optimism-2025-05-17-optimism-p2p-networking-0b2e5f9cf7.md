# Code-Shape Card

## Metadata

- ID: `optimism-2025-05-17-optimism-p2p-networking-0b2e5f9cf7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `forkchoice-state-handling`

## Code Shape Summary

- The buggy shape was a archive-extraction or file-materialization path that allowed data or state to approach filesystem write outside the intended extraction or artifact directory before fully enforcing path-confinement. The visible root cause is startup-state conflation: the pre-fix code promoted a newly inserted unsafe payload into stronger safe/finalized labels during EL sync, and the derivation actor's biased polling order gave a permanently-ready coordination future too much priority once closed.

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

- Separate startup sync handling from established forkchoice/finality handling, and prevent biased polling from giving a permanently-ready coordination future priority over normal state updates.

## False Match Warnings

- an earlier boundary already rejects the same malformed field under all reachable modes
- the changed code is test-only, generated-only, logging-only, or pure refactor with no runtime decision change
- the input is not attacker-influenced and cannot be affected by a faulty peer, operator, backend, or sequencer
- downstream consensus/proof verification recomputes the property fail-closed before any state or privilege is committed
