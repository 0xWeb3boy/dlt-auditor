# Code-Shape Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-sway-libs-arithmetic-correctness-bundle-32275`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `numeric-library-invariant-bundle`

## Code Shape Summary

- A broad set of math helpers used inconsistent widths, denominators, sign rules, and overflow behavior without a shared invariant test suite.

## Search Motifs

- i256 bits 128
- incorrect two's complement
- UFP32 fract underflow
- IFP ceil overflow

## Typical Asymmetry

- The vulnerable shape appears when one path carries a security, arithmetic, resource, or lifecycle invariant while a sibling path or generated artifact omits the same enforcement.
- Look for helper APIs, compiler metadata, opcode wrappers, or SDK state caches that are treated as authoritative by downstream code.

## Patch Pattern

- Define executable numeric invariants for each type family, fix each implementation to match them, and add cross-width edge-case tests.

## False Match Warnings

- A precision tradeoff is lower risk if documented and not used for settlement.
- A library bug is less severe when no reachable contract path uses the affected helper.
