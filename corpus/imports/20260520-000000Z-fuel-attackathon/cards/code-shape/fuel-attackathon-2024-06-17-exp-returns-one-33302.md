# Code-Shape Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-exp-returns-one-33302`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `fixed-point-exp-result-discarded`

## Code Shape Summary

- The return variable was the constant one even though the function computed a non-zero series adjustment.

## Search Motifs

- exp function always returns UFP128::from((1, 0))
- return one not one + res_minus_1
- fixed point exp incorrect

## Typical Asymmetry

- The vulnerable shape appears when one path carries a security, arithmetic, resource, or lifecycle invariant while a sibling path or generated artifact omits the same enforcement.
- Look for helper APIs, compiler metadata, opcode wrappers, or SDK state caches that are treated as authoritative by downstream code.

## Patch Pattern

- Return the computed exponential approximation and add non-zero test vectors with expected outputs.

## False Match Warnings

- No issue for e^0 only.
- No issue if the affected function is not exported or reachable in the used version.
