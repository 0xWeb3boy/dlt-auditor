# Root-Cause Card

## Metadata

- ID: `firedancer-2024-03-18-firedancer-transaction-processing-b39f4b4a3`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `vm-syscall-bounds-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `syscall-argument-and-budget-validation`

## Violated Invariant

- Invariant: VM syscalls must bound-check attacker-controlled slice counts, translated spans, and compute cost before copying or encoding log output.

## Trust Boundary

- Boundary: Untrusted program-supplied syscall arguments crossing into the VM runtime.

## Attack Surface

- Entrypoint type: smart-contract VM syscall
- Sensitive sink: log buffer construction and compute-budget accounting

## Impact Pattern

- Primary impact: denial of service
- Secondary impact: memory safety

## Short Reusable Lesson

- A logging syscall used user-controlled slice counts and translated memory spans before fully validating aggregate size, compute cost, and copy bounds.
