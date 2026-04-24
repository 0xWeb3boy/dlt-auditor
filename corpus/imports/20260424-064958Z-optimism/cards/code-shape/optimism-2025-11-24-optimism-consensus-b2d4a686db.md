# Code-Shape Card

## Metadata

- ID: `optimism-2025-11-24-optimism-consensus-b2d4a686db`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `protocol-invariant-enforcement`

## Code Shape Summary

- The buggy shape was a forkchoice/finality state-transition path that allowed data or state to approach safe/finalized head promotion, rewind, or consensus checkpoint update before fully enforcing input-validation. The visible issue is a logic mismatch between the intended deposit-only filtered attributes and the attributes object actually propagated through the build path.

## Search Motifs

- state promotion, rewind, or finalization proceeds without parent/canonicality/freshness check
- derivation updates persisted state before all protocol attributes are validated
- fork-specific validation is missing on one post-upgrade branch
- forkchoice/finality state-transition path reaches safe/finalized head promotion, rewind, or consensus checkpoint update with partial validation
- input-validation is enforced in one path but missing in an alternate path

## Typical Asymmetry

- The vulnerable asymmetry is that input-validation was enforced only partially, late, or in one lifecycle branch while another branch could still reach safe/finalized head promotion, rewind, or consensus checkpoint update.

## Patch Pattern

- Add a regression test for the intended filtered output, then make downstream runtime code consume the filtered attributes object consistently instead of another wrapper field.

## False Match Warnings

- an earlier boundary already rejects the same malformed field under all reachable modes
- the changed code is test-only, generated-only, logging-only, or pure refactor with no runtime decision change
- the input is not attacker-influenced and cannot be affected by a faulty peer, operator, backend, or sequencer
- downstream consensus/proof verification recomputes the property fail-closed before any state or privilege is committed
