# Root-Cause Card

## Metadata

- ID: `firedancer-2024-04-29-firedancer-transaction-processing-cf108c124`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `exact-authority-signer-validation`

## Violated Invariant

- Invariant: A privileged deploy or upgrade path must require the designated authority account itself to be marked as a signer before state changes occur.

## Trust Boundary

- Boundary: Transaction account metadata crossing into a privileged deploy/upgrade authorization gate.

## Attack Surface

- Entrypoint type: program deploy or upgrade authorization check
- Sensitive sink: program deployment or upgrade state transition

## Impact Pattern

- Primary impact: privilege misuse
- Secondary impact: none

## Short Reusable Lesson

- The authorization gate inferred signer status from indirect metadata rather than asking whether the specific authority account index was actually a signer.
