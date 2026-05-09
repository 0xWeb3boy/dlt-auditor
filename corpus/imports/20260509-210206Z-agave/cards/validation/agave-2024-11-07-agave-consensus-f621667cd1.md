# Validation Card

## Metadata

- ID: `agave-2024-11-07-agave-consensus-f621667cd1`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unauthenticated-constructor-exposure`

## What Confirmed The Issue

- The signed constructor now serializes data and signs with a keypair.
- The unsigned constructor is restricted to cfg(test) pub(crate).

## What Could Have Invalidated It

- Production code never had access to the unsigned constructor.
- A mandatory verification gate rejects any unsigned value before insertion or broadcast.

## Severity Guidance

- Expected impact band: `authenticity hardening`
- Expected severity band: `low`
- Rationale: The patch removes an unsafe construction footgun in a signed gossip type, but the evidence did not show a production misuse or remote acceptance bypass.

## False-Positive Cautions

- Constructor hardening is often a preventive API fix, not proof of a remote vulnerability.
- Do not claim consensus failure unless unsigned values can actually enter verified gossip state.
