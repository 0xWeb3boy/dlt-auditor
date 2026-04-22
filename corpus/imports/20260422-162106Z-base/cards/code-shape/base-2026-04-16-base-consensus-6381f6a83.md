# Code-Shape Card

## Metadata

- ID: `base-2026-04-16-base-consensus-6381f6a83`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `challenge-fallback-liveness`

## Code Shape Summary

- Short description of what the buggy code looked like: The pending-proof and retry logic for TEE proofs did not preserve or use the information needed to transition from a failed TEE submission into the alternate ZK path. This is a state-management and retry-flow defect, not evidence of a cryptographic or consensus flaw.

## Search Motifs

- Motif 1: challenge mode handled by a generic validation branch instead of the challenged case
- Motif 2: decision logic derives the target index or root from the wrong proof element
- Motif 3: retry or fallback state is dropped before the dispute path reaches a definitive decision

## Typical Asymmetry

- What was checked in one path but missing in another: The generic challenge machinery was present, but the branch for the specific challenged proof, root, or fallback transition reused the wrong validation rule or dropped the needed state.

## Patch Pattern

- What the fix changed structurally: Preserve alternate-path state at creation time and make retry handling perform an explicit state transition to that fallback path instead of retrying the original path indefinitely or discarding the work item.

## False Match Warnings

- What looks similar but is often not a bug: Treat this as hardening of challenger/dispute liveness, not as proof of an exploitable protocol vulnerability.
