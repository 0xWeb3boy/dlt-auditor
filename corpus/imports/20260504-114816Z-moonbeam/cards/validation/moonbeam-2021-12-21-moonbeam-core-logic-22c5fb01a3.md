# Validation Card

## Metadata

- ID: `moonbeam-2021-12-21-moonbeam-core-logic-22c5fb01a3`
- Bug family: `authz_and_role_gates`
- Bug class: `state-corruption`

## What Confirmed The Issue

- Patch adds ensure MappingWithDeposit(new_author_id).is_none before insertion.
- Regression tests assert AlreadyAssociated for occupied destination updates.

## What Could Have Invalidated It

- Storage insert was already non-overwriting or transactional with an occupied-key error
- Only root/governance could call the update path

## Severity Guidance

- Expected impact band: authorization_state_integrity
- Expected severity band: high

## False-Positive Cautions

- Overwrite may be safe if insert is known to fail on occupied keys
- Destination may be protected by a unique index checked in a lower layer
