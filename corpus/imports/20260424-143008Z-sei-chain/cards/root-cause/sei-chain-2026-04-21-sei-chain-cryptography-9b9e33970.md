# Root-Cause Card

## Metadata

- ID: `sei-chain-2026-04-21-sei-chain-cryptography-9b9e33970`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `secret-key-lifecycle-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `secret-key-runtime-lifecycle`

## Violated Invariant

- Invariant: Secret key memory must remain reachable during signing and must not be retained accidentally by cleanup hooks after intended disposal.

## Trust Boundary

- Boundary: application signing code -> cryptographic secret key memory/runtime cleanup

## Attack Surface

- Entrypoint type: secret-key-signing-method
- Sensitive sink: using and cleaning private key material

## Impact Pattern

- Primary impact: secret-key-exposure-risk-reduction
- Secondary impact: memory-lifecycle-hardening

## Short Reusable Lesson

- Harden cryptographic secret lifecycle handling by making runtime reachability explicit, avoiding cleanup callbacks that retain the object being cleaned, hiding raw secret pointers behind a private accessor, and keeping key objects alive until signing. Affects Ed25519 private-key storage and signing code. Improves alignment with Go runtime cleanup reachability rules.
