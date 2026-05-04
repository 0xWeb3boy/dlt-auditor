# Validation Card

## Metadata

- ID: `moonbeam-2021-12-21-moonbeam-core-logic-a427c2b20a`
- Bug family: `authz_and_role_gates`
- Bug class: `association-integrity`

## What Confirmed The Issue

- New ensure rejects existing new_author_id with AlreadyAssociated.
- Tests changed from accepting self/existing update to expecting failure.

## What Could Have Invalidated It

- The old update path never inserted into the destination after removal
- The mapping semantics intentionally supported reassignment by current owner of both keys

## Severity Guidance

- Expected impact band: authorization_state_integrity
- Expected severity band: high

## False-Positive Cautions

- Destination collisions are harmless if aliases are intentionally allowed
- A lower-layer reservation map may enforce uniqueness already
