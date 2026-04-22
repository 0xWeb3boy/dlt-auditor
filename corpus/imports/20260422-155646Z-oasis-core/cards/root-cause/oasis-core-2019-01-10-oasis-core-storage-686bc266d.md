# Root-Cause Card

## Metadata

- ID: `oasis-core-2019-01-10-oasis-core-storage-686bc266d`
- Bug family: `authz_and_role_gates`
- Bug class: `improper-authorization-check`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `authorization`

## Violated Invariant

- Invariant: Committee-related messages and external batches should only be accepted from authorized peers and only when the local worker is in the expected role and state for that path.

## Trust Boundary

- Boundary: `peer->node`

## Attack Surface

- Entrypoint type: `p2p-message-handler`
- Sensitive sink: `security-sensitive consensus or registry state`

## Impact Pattern

- Primary impact: `unauthorized-message-processing`
- Secondary impact: `none`

## Short Reusable Lesson

- Committee-related messages and external batches should only be accepted from authorized peers and only when the local worker is in the expected role and state for that path. In this pattern, the evidence supports only a narrow conclusion: authorization and state validation were not enforced as early or as uniformly as the updated code now enforces them. It does not prove a concrete exploitable root cause beyond that. The robust fix is to make the privileged sink consume the canonical identity, state coordinate, or accounting result directly and to fail closed when that binding is missing.
