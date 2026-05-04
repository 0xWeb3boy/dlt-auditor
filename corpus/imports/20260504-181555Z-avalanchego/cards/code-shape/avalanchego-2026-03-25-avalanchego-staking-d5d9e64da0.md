# Code-Shape Card

## Metadata

- ID: `avalanchego-2026-03-25-avalanchego-staking-d5d9e64da0`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `unchecked-validator-weight-overflow`

## Code Shape Summary

- Auto-renewed validator weight reconstruction changed from unchecked uint64 addition to checked safemath additions. The reusable shape is persisted accounting state reconstructed by summing bounded integer fields before use in validator power or reward logic.

## Search Motifs

- stakerTx.Weight plus accrued rewards computed with +
- safemath.Add introduced around validator or reward accounting
- overflow computing weight returned from state loading

## Typical Asymmetry

- The sensitive sink is protected in some paths or under some fork/configuration states, while a neighboring path, boundary case, or compatibility exception omits the same property.
- The vulnerable-looking code often appears as a small predicate, arithmetic expression, allowlist exception, or proof/header check near a much larger protocol feature.

## Patch Pattern

- Replace direct integer addition with checked arithmetic and propagate overflow errors before updating validator state.
- Add focused regression tests for the boundary case, not only broad happy-path coverage.

## False Match Warnings

- If protocol caps prove the sum cannot overflow, this is defense-in-depth
- Do not claim consensus split without divergent state evidence
- Tests around helpers are support evidence, not proof of exploitability
