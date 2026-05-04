# Code-Shape Card

## Metadata

- ID: `moonbeam-2021-12-21-moonbeam-core-logic-a427c2b20a`
- Bug family: `authz_and_role_gates`
- Bug class: `association-integrity`

## Code Shape Summary

- A mapping update treated source ownership as sufficient authorization for a destination key. The fix rejects occupied destination keys before removing or inserting association state.

## Search Motifs

- source owner check but no destination contains_key check
- association rename into caller-selected existing key
- AlreadyAssociated added to update path tests

## Typical Asymmetry

- The accepting path trusted a local or current-state predicate, while the sensitive sink required a stronger global, historical, caller-class, domain, or cumulative invariant.

## Patch Pattern

- Fail closed on occupied destination ids and preserve existing associations by checking uniqueness before mutation.

## False Match Warnings

- Destination collisions are harmless if aliases are intentionally allowed
- A lower-layer reservation map may enforce uniqueness already
- Admin-only migration code has different threat model
