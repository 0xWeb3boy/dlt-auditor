# Code-Shape Card

## Metadata

- ID: `optimism-2026-03-04-optimism-consensus-23f3ffea2a`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-safety`

## Code Shape Summary

- The buggy shape was a forkchoice/finality state-transition path that allowed data or state to approach safe/finalized head promotion, rewind, or consensus checkpoint update before fully enforcing protocol-state-invariant. The status-handling logic did not distinguish expected SYNCING during initial execution-layer sync from unexpected SYNCING after sync had already completed, so a post-sync loss of EL state could be treated as success rather than as desynchronization.

## Search Motifs

- state promotion, rewind, or finalization proceeds without parent/canonicality/freshness check
- derivation updates persisted state before all protocol attributes are validated
- fork-specific validation is missing on one post-upgrade branch
- forkchoice/finality state-transition path reaches safe/finalized head promotion, rewind, or consensus checkpoint update with partial validation
- protocol-state-invariant is enforced in one path but missing in an alternate path

## Typical Asymmetry

- The vulnerable asymmetry is that protocol-state-invariant was enforced only partially, late, or in one lifecycle branch while another branch could still reach safe/finalized head promotion, rewind, or consensus checkpoint update.

## Patch Pattern

- Make status handling stateful at the forkchoice boundary: allow a transient status during bootstrap, but treat the same status as an error after the subsystem has transitioned into steady state.

## False Match Warnings

- an earlier boundary already rejects the same malformed field under all reachable modes
- the changed code is test-only, generated-only, logging-only, or pure refactor with no runtime decision change
- the input is not attacker-influenced and cannot be affected by a faulty peer, operator, backend, or sequencer
- downstream consensus/proof verification recomputes the property fail-closed before any state or privilege is committed
