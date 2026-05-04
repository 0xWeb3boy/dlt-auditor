# Root-Cause Card

## Metadata

- ID: `moonbeam-2021-12-21-moonbeam-core-logic-a427c2b20a`
- Bug family: `authz_and_role_gates`
- Bug class: `association-integrity`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `destination-key-uniqueness`

## Violated Invariant

- Invariant: A rename/update operation must prove both source ownership and destination availability before mutating a shared identity map.

## Trust Boundary

- Boundary: Signed account ownership of one association crosses into global author-id namespace mutation.

## Attack Surface

- Entrypoint type: registration-update-extrinsic
- Sensitive sink: author mapping registration storage

## Impact Pattern

- Primary impact: state-integrity
- Secondary impact: unauthorized-action, identity-takeover

## Short Reusable Lesson

- A mapping update treated source ownership as sufficient authorization for a destination key. The fix rejects occupied destination keys before removing or inserting association state. Fail closed on occupied destination ids and preserve existing associations by checking uniqueness before mutation.
