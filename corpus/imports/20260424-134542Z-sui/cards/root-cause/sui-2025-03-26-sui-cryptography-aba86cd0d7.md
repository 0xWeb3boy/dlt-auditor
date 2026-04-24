# Root-Cause Card

## Metadata

- ID: `sui-2025-03-26-sui-cryptography-aba86cd0d7`
- Bug family: `authz_and_role_gates`
- Bug class: `missing-consensus-object-ownership-authentication`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `authorization`

## Violated Invariant

- Invariant: Object ownership and access checks must be enforced before a transaction can read, mutate, or consume object state.

## Trust Boundary

- Boundary: signed payload or certificate bytes -> trust decision

## Attack Surface

- Entrypoint type: signature-verification-path
- Sensitive sink: authorizing object access or privileged state mutation

## Impact Pattern

- Primary impact: unauthorized-object-use
- Secondary impact: transaction-input-authorization-bypass

## Short Reusable Lesson

- Authorization must be checked at the boundary where authority is consumed, not inferred from caller-controlled fields or earlier best-effort filters. The evidence supports a likely security fix in Sui transaction input validation for ConsensusV2 objects. The commit message says object ownership is now verified at signing time, and the diff adds access to ConsensusV2 authenticator metadata while separating ConsensusV2 handling from ordinary shared-object version checks.
