# Root-Cause Card

## Metadata

- ID: `nitro-2023-12-11-nitro-cryptography-1d3b655ea`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incomplete-state-commitment`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `complete-state-commitment`

## Violated Invariant

- Invariant: State commitments should include every mode bit that changes behavior, even when the associated collection or stack is empty.

## Trust Boundary

- Boundary: `machine state->hash or state commitment`

## Attack Surface

- Entrypoint type: `state-commitment-computation`
- Sensitive sink: `accepting or comparing a machine state hash`

## Impact Pattern

- Primary impact: `integrity`
- Secondary impact: `none`

## Short Reusable Lesson

- State commitments should include every mode bit that changes behavior, even when the associated collection or stack is empty. The strongest supported finding is a prover state-hash correctness fix: `Machine::hash` now commits the guard-enabled flag even when the guard stack is empty, and `ErrorGuardProof::hash_guards` no longer mixes that flag into the stack-hash helper. The robust fix is to make the privileged sink consume authoritative state or policy context that has already been validated, and fail closed when that binding is missing.
