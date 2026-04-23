# Root-Cause Card

## Metadata

- ID: `nitro-2023-11-21-nitro-core-logic-995df9e00`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `error-handling-policy`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `explicit-error-recovery-policy`

## Violated Invariant

- Invariant: Exceptional recovery should be controlled by explicit policy state, not by the mere presence of leftover internal frames or stacks.

## Trust Boundary

- Boundary: `internal VM state->error recovery decision`

## Attack Surface

- Entrypoint type: `exception-handling-or-recovery`
- Sensitive sink: `resuming execution under an error-recovery guard`

## Impact Pattern

- Primary impact: `execution-integrity`
- Secondary impact: `none`

## Short Reusable Lesson

- Exceptional recovery should be controlled by explicit policy state, not by the mere presence of leftover internal frames or stacks. The patch changes the prover VM's error-guard behavior from implicitly recovering whenever a guard frame exists to recovering only when an explicit `enabled` policy bit is set. That is a real control-flow hardening change, but the provided evidence does not establish a concrete vulnerability, attacker trigger, or protocol impact. The robust fix is to make the privileged sink consume authoritative state or policy context that has already been validated, and fail closed when that binding is missing.
