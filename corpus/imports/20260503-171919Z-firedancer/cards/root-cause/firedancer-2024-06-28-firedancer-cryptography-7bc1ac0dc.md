# Root-Cause Card

## Metadata

- ID: `firedancer-2024-06-28-firedancer-cryptography-7bc1ac0dc`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unchecked-cryptographic-rng-failure`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `rng-failure-handling`

## Violated Invariant

- Invariant: Randomly generated identifiers used in protocol state must abort the operation if entropy generation fails.

## Trust Boundary

- Boundary: OS or helper RNG results crossing into connection-ID generation.

## Attack Surface

- Entrypoint type: connection initialization helper
- Sensitive sink: connection ID issuance and state setup

## Impact Pattern

- Primary impact: connection id randomness integrity
- Secondary impact: fail open on rng failure

## Short Reusable Lesson

- Protocol setup called a random-byte helper for connection identifiers without checking the documented failure path.
