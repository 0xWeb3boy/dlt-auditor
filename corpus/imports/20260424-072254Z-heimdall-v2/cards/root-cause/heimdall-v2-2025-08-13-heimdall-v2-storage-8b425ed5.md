# Root-Cause Card

## Metadata

- ID: `heimdall-v2-2025-08-13-heimdall-v2-storage-8b425ed5`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `checkpoint-chain-id-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: chain-domain validation at checkpoint side-vote boundary.

## Violated Invariant

- Invariant: a validator side-vote handler must only approve checkpoint data for the configured source chain or domain, and must fail closed if domain configuration cannot be read.

## Trust Boundary

- Boundary: checkpoint message carrying a chain identifier crossing into validator side-vote validation.

## Attack Surface

- Entrypoint type: consensus side-message vote handler.
- Sensitive sink: validator YES/NO vote for checkpoint validity.

## Impact Pattern

- Primary impact: checkpoint domain separation.
- Secondary impact: cross-chain replay or confusion resistance.

## Short Reusable Lesson

- Cross-chain handlers should compare message domain identifiers against trusted local configuration before deeper validation. If configuration cannot be loaded, the safe vote or decision is rejection, not best-effort validation.
