# Code-Shape Card

## Metadata

- ID: `moonbeam-2021-12-21-moonbeam-core-logic-22c5fb01a3`
- Bug family: `authz_and_role_gates`
- Bug class: `state-corruption`

## Code Shape Summary

- The update path verified the caller owned old_author_id, then inserted state at caller-controlled new_author_id without first proving the destination was unoccupied.

## Search Motifs

- update_association(old_id, new_id) checks old owner only
- insert(new_key, existing_info) without contains_key(new_key)
- remove old mapping before/without destination uniqueness guard

## Typical Asymmetry

- The accepting path trusted a local or current-state predicate, while the sensitive sink required a stronger global, historical, caller-class, domain, or cumulative invariant.

## Patch Pattern

- Add a destination vacancy guard before removing the old mapping or inserting into the new key.

## False Match Warnings

- Overwrite may be safe if insert is known to fail on occupied keys
- Destination may be protected by a unique index checked in a lower layer
- Self-renaming to the same key may need special handling but is not takeover
