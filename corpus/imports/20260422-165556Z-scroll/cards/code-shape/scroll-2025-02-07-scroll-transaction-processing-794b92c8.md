# Code-Shape Card

## Metadata

- ID: `scroll-2025-02-07-scroll-transaction-processing-794b92c8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-compatibility-check`

## Code Shape Summary

- Short description of what the buggy code looked like: The patch re-enables a fork-compatibility check in three prover-task assignment paths. The evidence shows the coordinator previously had this guard commented out and now rejects assignment when the prover does not advertise support for the task's required hard fork. That establishes a real correctness and safety check was restored, but the provided material does not prove a concrete security vulnerability or downstream acceptance of invalid proofs.

## Search Motifs

- Motif 1: compatibility check exists but is commented out in task assignment paths
- Motif 2: hard fork name available in task context but not enforced against prover capabilities
- Motif 3: multiple assignment paths duplicate capability gating and one or more silently skip it

## Typical Asymmetry

- What was checked in one path but missing in another: One path or representation enforced the canonical rule, identity, or compatibility gate while another parallel path, legacy branch, or helper-derived value reached the sink without the same binding.

## Patch Pattern

- What the fix changed structurally: Restore fail-closed hard-fork capability checks in every prover-task assignment path before dispatching chunk, batch, or bundle work.

## False Match Warnings

- Warning 1: If downstream verifiers or provers reject mismatched tasks before any stateful effect, similar bugs may be operational rather than security-relevant.
- Warning 2: Presence of a capability map alone is not enough; the key issue is whether every assignment path enforces it before dispatch.
- Warning 3: The evidence supports safety gating restoration, not a demonstrated invalid-proof acceptance bug.
