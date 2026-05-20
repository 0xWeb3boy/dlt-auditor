# Code-Shape Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-cross-contract-stack-overflow-33519`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `stack-frame-overwrite-across-calls`

## Code Shape Summary

- Generated code for complex cross-contract calls could place large locals in stack regions without a reliable overflow guard.

## Search Motifs

- u256 locals around contract call
- stack overflow silent
- call frame size calculation
- adjacent variable overwritten

## Typical Asymmetry

- The vulnerable shape appears when one path carries a security, arithmetic, resource, or lifecycle invariant while a sibling path or generated artifact omits the same enforcement.
- Look for helper APIs, compiler metadata, opcode wrappers, or SDK state caches that are treated as authoritative by downstream code.

## Patch Pattern

- Enforce stack-frame bounds during code generation or VM execution, trap on overflow, and add regression tests around wide locals across contract calls.

## False Match Warnings

- A trapped stack overflow with no state commitment is not this issue.
- Purely local corruption in a test harness is lower risk without a reachable contract path.
