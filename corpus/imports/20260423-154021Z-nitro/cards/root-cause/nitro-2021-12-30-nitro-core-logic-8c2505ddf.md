# Root-Cause Card

## Metadata

- ID: `nitro-2021-12-30-nitro-core-logic-8c2505ddf`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-state-management`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `immutable-state-handling`

## Violated Invariant

- Invariant: Shared or frozen validator/prover machine state should be cloned from a fresh canonical base object and mutators should fail closed when the target machine is immutable.

## Trust Boundary

- Boundary: `shared machine handle->validator or prover mutation logic`

## Attack Surface

- Entrypoint type: `state-transition-or-machine-management`
- Sensitive sink: `mutation of validator or prover machine state`

## Impact Pattern

- Primary impact: `state-integrity`
- Secondary impact: `none`

## Short Reusable Lesson

- Shared or frozen validator/prover machine state should be cloned from a fresh canonical base object and mutators should fail closed when the target machine is immutable. The supplied diff supports validator-machine state-management hardening: validation now fetches a host-IO machine before cloning, and mutators now reject frozen machines. The evidence does not establish a concrete vulnerability, attacker trigger, or protocol-level security failure. The robust fix is to make the privileged sink consume authoritative state or policy context that has already been validated, and fail closed when that binding is missing.
