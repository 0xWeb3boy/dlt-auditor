# Root-Cause Card

## Metadata

- ID: `moonbeam-2021-12-21-moonbeam-core-logic-22c5fb01a3`
- Bug family: `authz_and_role_gates`
- Bug class: `state-corruption`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `destination-key-uniqueness`

## Violated Invariant

- Invariant: Ownership of one registered object must not authorize overwriting or taking over another already-registered object.

## Trust Boundary

- Boundary: A signed owner update crosses from a private association into shared validator/author identity storage.

## Attack Surface

- Entrypoint type: registration-update-extrinsic
- Sensitive sink: author mapping registration storage

## Impact Pattern

- Primary impact: state-integrity
- Secondary impact: unauthorized-action, identity-takeover

## Short Reusable Lesson

- The update path verified the caller owned old_author_id, then inserted state at caller-controlled new_author_id without first proving the destination was unoccupied. Add a destination vacancy guard before removing the old mapping or inserting into the new key.
