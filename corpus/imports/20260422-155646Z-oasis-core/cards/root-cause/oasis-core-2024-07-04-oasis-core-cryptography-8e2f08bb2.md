# Root-Cause Card

## Metadata

- ID: `oasis-core-2024-07-04-oasis-core-cryptography-8e2f08bb2`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `authorization`

## Violated Invariant

- Invariant: CHURP key-share query handling should apply explicit authorization rules tied to runtime/policy context, and consensus should not admit 'MayQuery' policy state before the protocol version that defines and supports it.

## Trust Boundary

- Boundary: `client->query-verifier`

## Attack Surface

- Entrypoint type: `query-verification-path`
- Sensitive sink: `key-share release or secret-state acceptance`

## Impact Pattern

- Primary impact: `privilege-misuse`
- Secondary impact: `none`

## Short Reusable Lesson

- CHURP key-share query handling should apply explicit authorization rules tied to runtime/policy context, and consensus should not admit 'MayQuery' policy state before the protocol version that defines and supports it. In this pattern, the shown code indicates an under-specified authorization boundary for key-share queries and missing admission-time validation for a policy field related to query authorization semantics. The robust fix is to make the privileged sink consume the canonical identity, state coordinate, or accounting result directly and to fail closed when that binding is missing.
