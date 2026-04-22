# Root-Cause Card

## Metadata

- ID: `oasis-core-2019-08-23-oasis-core-rpc-client-api-4333549d8`
- Bug family: `authz_and_role_gates`
- Bug class: `missing-authentication`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `authentication`

## Violated Invariant

- Invariant: The IAS VerifyEvidence RPC must not accept a request solely because its SignedEvidence blob parses; it must also enforce the configured attestation policy for the caller and decoded evidence before proceeding.

## Trust Boundary

- Boundary: `remote-peer->rpc-verifier`

## Attack Surface

- Entrypoint type: `rpc-handler`
- Sensitive sink: `attestation acceptance state`

## Impact Pattern

- Primary impact: `unauthorized-request-processing`
- Secondary impact: `attestation-policy-bypass`

## Short Reusable Lesson

- The IAS VerifyEvidence RPC must not accept a request solely because its SignedEvidence blob parses; it must also enforce the configured attestation policy for the caller and decoded evidence before proceeding. In this pattern, a security-sensitive RPC handler relied on comments describing required authorization and attestation-policy checks instead of enforcing those checks in code after parsing the request. The robust fix is to make the privileged sink consume the canonical identity, state coordinate, or accounting result directly and to fail closed when that binding is missing.
