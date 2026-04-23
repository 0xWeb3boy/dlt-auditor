# Root-Cause Card

## Metadata

- ID: `nitro-2022-02-21-nitro-transaction-processing-9d6ff6021`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-state-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `canonical-state-consistency-check`

## Violated Invariant

- Invariant: Validator branch traversal should verify that a looked-up node still matches the expected canonical hash before deriving children or creating new nodes from it.

## Trust Boundary

- Boundary: `persisted validator tree state->branch traversal and node creation`

## Attack Surface

- Entrypoint type: `validator-state-traversal`
- Sensitive sink: `child traversal or new-node creation on validator state`

## Impact Pattern

- Primary impact: `state-integrity`
- Secondary impact: `none`

## Short Reusable Lesson

- Validator branch traversal should verify that a looked-up node still matches the expected canonical hash before deriving children or creating new nodes from it. The visible patch is best supported as validator correctness hardening. It adds a node-hash consistency check before child traversal and narrows when new-node creation is attempted, but the provided evidence does not establish a concrete vulnerability or a definite security impact. The robust fix is to make the privileged sink consume authoritative state or policy context that has already been validated, and fail closed when that binding is missing.
