# Root-Cause Card

## Metadata

- ID: `oasis-core-2023-04-12-oasis-core-cryptography-97f265501`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `untrusted-secret-validation`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `secret-state-validation`

## Violated Invariant

- Invariant: Replicated or persisted master-secret state should only affect rotation when it is bound to the correct runtime and generation and matches the expected checksum chain; replicated values are untrusted until verified.

## Trust Boundary

- Boundary: `peer->node`

## Attack Surface

- Entrypoint type: `state-transition`
- Sensitive sink: `key-share release or secret-state acceptance`

## Impact Pattern

- Primary impact: `integrity-risk`
- Secondary impact: `none`

## Short Reusable Lesson

- Replicated or persisted master-secret state should only affect rotation when it is bound to the correct runtime and generation and matches the expected checksum chain; replicated values are untrusted until verified. In this pattern, the supported evidence points to weaker pre-patch state selection and scoping in the rotation path: the code depended on a single fetched master-secret candidate, and the shown proposal helper API was less explicitly bound to runtime and generation. That supports a narrow thesis of validation/scoping hardening, but not a proven exploitable vulnerability. The robust fix is to make the privileged sink consume the canonical identity, state coordinate, or accounting result directly and to fail closed when that binding is missing.
