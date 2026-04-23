# Root-Cause Card

## Metadata

- ID: `nitro-2023-07-31-nitro-transaction-processing-dd22b5f05`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validator-state-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `canonical-validator-state-derivation`

## Violated Invariant

- Invariant: State-derived hashes and message counts should be computed only from canonical boundary states and domain-separated commitments.

## Trust Boundary

- Boundary: `validator state and proof inputs->message-count and hash derivation`

## Attack Surface

- Entrypoint type: `proof-or-state-derivation`
- Sensitive sink: `deriving assertion, proof, or validator hashes from state`

## Impact Pattern

- Primary impact: `state-integrity`
- Secondary impact: `none`

## Short Reusable Lesson

- State-derived hashes and message counts should be computed only from canonical boundary states and domain-separated commitments. The patch tightens how the staker/validator path interprets execution state when deriving message counts and hashes. The evidence supports a protocol-correctness or hardening change, but it does not establish an exploitable vulnerability from the provided diff alone. The robust fix is to make the privileged sink consume authoritative state or policy context that has already been validated, and fail closed when that binding is missing.
