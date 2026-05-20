# Root-Cause Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-wide-compare-register-cleanup-32768`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `reserved-register-stale-state`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `reserved-register-cleanup`

## Violated Invariant

- Each VM instruction must leave reserved status registers exactly as specified, independent of previous instructions.

## Trust Boundary

- Boundary: `previous-instruction-state->current-instruction-state`
- Entrypoint type: `vm-opcode`
- Sensitive sink: `stale err/of registers consumed by later bytecode`

## Attack Surface

- Set err or of with an earlier instruction.
- Execute WDCM or WQCM and branch on the stale register value.

## Exploit Preconditions

- The spec requires WDCM and WQCM to clear err and of.
- The implementation updates comparison output but leaves status registers unchanged.

## Impact Pattern

- Primary impact: `state-integrity`
- Secondary impact: `contract-behavior-integrity`
- Blast radius: `chain-wide`
- Severity guess: `medium`

## Short Reusable Lesson

- Instruction conformance includes cleanup of implicit machine state, not only the explicit destination register.
