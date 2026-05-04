# Root-Cause Card

## Metadata

- ID: `stacks-core-2017-08-02-stacks-core-storage-af0f3c9ad5`
- Bug family: `authz_and_role_gates`
- Bug class: `address-bound-authorization-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `authorization-to-state-binding`

## Violated Invariant

- Invariant: Only principals with the role, address ownership, or delegated authority required for a state transition may cause that transition to be accepted.

## Trust Boundary

- Boundary: Persisted or peer-derived chain state crosses into storage-backed validation.

## Attack Surface

- Entrypoint type: `state_database_lookup_or_update`
- Sensitive sink: canonical state database, cached validation state, or durable index

## Impact Pattern

- Primary impact: authorization-bypass-risk
- Secondary impact: unauthorized-state-mutation

## Short Reusable Lesson

- The patch is security relevant but the vulnerability thesis is not established by the supplied evidence. The grounded evidence shows subdomain code moving from pubkey-oriented handling toward Bitcoin-address-based ownership, address-bound mutable-data lookup, and scriptSig-style verification. However, the full update acceptance path, validation outcome, and attacker capability are not shown, so this should not be treated as a confirmed vulnerability fix.
