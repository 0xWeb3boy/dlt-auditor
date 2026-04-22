# Code-Shape Card

## Metadata

- ID: `base-2026-04-16-base-rpc-client-api-6d1cabf2b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incorrect-fraud-challenge-validation`

## Code Shape Summary

- Short description of what the buggy code looked like: The challenger used validation scope that was broader than the decision boundary for this path. It considered all intermediate roots and derived the outcome from the first invalid one encountered, even though the dispute state identifies one specific challenged intermediate root index.

## Search Motifs

- Motif 1: challenge mode handled by a generic validation branch instead of the challenged case
- Motif 2: decision logic derives the target index or root from the wrong proof element
- Motif 3: retry or fallback state is dropped before the dispute path reaches a definitive decision

## Typical Asymmetry

- What was checked in one path but missing in another: The generic challenge machinery was present, but the branch for the specific challenged proof, root, or fallback transition reused the wrong validation rule or dropped the needed state.

## Patch Pattern

- What the fix changed structurally: Replace collection-wide heuristic validation with targeted validation of the exact protocol-selected item.

## False Match Warnings

- What looks similar but is often not a bug: This supports a security-relevant hardening in off-chain challenger dispute handling.
