# Root-Cause Card

## Metadata

- ID: `oasis-core-2020-01-29-oasis-core-cryptography-f8809788d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: Registry admission should reject descriptors that are internally malformed or inconsistent with role and runtime-reference constraints before they enter registry or genesis state.

## Trust Boundary

- Boundary: `operator->registry`

## Attack Surface

- Entrypoint type: `registration-path`
- Sensitive sink: `security-sensitive consensus or registry state`

## Impact Pattern

- Primary impact: `correctness-or-hardening`
- Secondary impact: `none`

## Short Reusable Lesson

- Registry admission should reject descriptors that are internally malformed or inconsistent with role and runtime-reference constraints before they enter registry or genesis state. In this pattern, incomplete registry admission sanity checks: some descriptor constraints were either not enforced in the shown path or were only checked after insufficient context had been assembled. The robust fix is to make the privileged sink consume the canonical identity, state coordinate, or accounting result directly and to fail closed when that binding is missing.
