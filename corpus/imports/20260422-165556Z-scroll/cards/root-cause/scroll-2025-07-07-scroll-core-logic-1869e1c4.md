# Root-Cause Card

## Metadata

- ID: `scroll-2025-07-07-scroll-core-logic-1869e1c4`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `canonical-input-normalization`

## Violated Invariant

- Invariant: Universal task generation should normalize and compare fork identifiers before deriving proving inputs from both serialized task JSON and separate fork arguments.

## Trust Boundary

- Boundary: `task-json->universal-task-builder`

## Attack Surface

- Entrypoint type: `state-transition`
- Sensitive sink: `constructed universal proving task passed into proof generation or verification`

## Impact Pattern

- Primary impact: `state-integrity`
- Secondary impact: `none`

## Short Reusable Lesson

- Universal task generation should normalize and compare fork identifiers before deriving proving inputs from both serialized task JSON and separate fork arguments. The patch in `crates/libzkp/src/lib.rs` adds canonicalization and an equality check for `fork_name` when building chunk and batch universal tasks. The code evidence supports a consistency fix at a protocol-sensitive boundary, but it does not establish that this previously enabled invalid proof acceptance, verifier bypass, or another concrete vulnerability. The robust fix is to normalize fork-name aliases and reject cross-field mismatches before building chunk or batch universal tasks from mixed task sources.
