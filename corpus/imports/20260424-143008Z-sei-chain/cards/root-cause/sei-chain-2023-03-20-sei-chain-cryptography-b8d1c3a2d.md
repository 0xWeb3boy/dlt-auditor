# Root-Cause Card

## Metadata

- ID: `sei-chain-2023-03-20-sei-chain-cryptography-b8d1c3a2d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `merkle-proof-structural-validation`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `proof-structure-rejection`

## Violated Invariant

- Invariant: Cryptographic proof reconstruction must reject malformed proof shapes explicitly before any root or membership result is accepted.

## Trust Boundary

- Boundary: untrusted Merkle proof bytes -> trusted root or membership decision

## Attack Surface

- Entrypoint type: proof-verification-function
- Sensitive sink: accepting proof output or returning reconstructed root

## Impact Pattern

- Primary impact: integrity
- Secondary impact: proof-forgery-prevention

## Short Reusable Lesson

- Replace sentinel nil results in cryptographic proof reconstruction with explicit errors, then require all proof verification/output callers to propagate those errors before accepting or returning a root. Malformed Merkle proof structures are rejected explicitly. Verification no longer treats reconstruction failure as an ordinary computed hash value.
