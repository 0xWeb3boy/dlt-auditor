# Code-Shape Card

## Metadata

- ID: `agave-2024-11-07-agave-consensus-f621667cd1`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unauthenticated-constructor-exposure`

## Code Shape Summary

- A signed gossip value type exposed both signed and unsigned constructors in production, leaving the authenticity invariant to caller discipline instead of the type interface.

## Search Motifs

- public new_unsigned constructor on signed network message
- default signature value outside cfg(test)
- constructor for authenticated gossip value without keypair
- test helper exposed as production API

## Typical Asymmetry

- The vulnerable shape trusts an earlier, broader, or non-consuming check while a later security-sensitive sink assumes the data, identity, quota, or state was fully validated.
- The fixed shape moves the check to the boundary that owns the sink, consumes/accounting resources at admission, or carries authenticity/state metadata forward explicitly.

## Patch Pattern

- Make the signed constructor the public production path and restrict unsigned construction helpers to test-only/internal visibility.

## False Match Warnings

- Unsigned constructors are cfg(test), private, or impossible to call in production.
- Every production insertion path independently signs or verifies before use.
- The type is purely local test data and never crosses a network or consensus boundary.
