# Root-Cause Card

## Metadata

- ID: `scroll-2025-07-07-scroll-core-logic-7f081d66`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `canonical-input-normalization`

## Violated Invariant

- Invariant: Universal task generation should canonicalize fork names and reject inconsistent fork identity before deriving proving inputs from mixed task sources.

## Trust Boundary

- Boundary: `task-json->universal-task-builder`

## Attack Surface

- Entrypoint type: `state-transition`
- Sensitive sink: `constructed universal proving task passed into proof generation or verification`

## Impact Pattern

- Primary impact: `state-integrity`
- Secondary impact: `none`

## Short Reusable Lesson

- Universal task generation should canonicalize fork names and reject inconsistent fork identity before deriving proving inputs from mixed task sources. The patch adds fork-name normalization and an equality check in `gen_universal_task`, so chunk and batch tasks no longer proceed with an unchecked combination of `task_json` fork data and a separate fork-name string. The evidence supports a correctness/integrity fix around inconsistent fork-name handling, but it does not establish a concrete vulnerability or prior acceptance of invalid proofs. The robust fix is to normalize fork-name variants and fail closed when task JSON and explicit fork arguments disagree before generating universal tasks.
