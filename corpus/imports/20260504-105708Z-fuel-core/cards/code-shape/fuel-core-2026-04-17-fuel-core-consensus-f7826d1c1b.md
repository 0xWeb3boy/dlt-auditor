# Code-Shape Card

## Metadata

- ID: `fuel-core-2026-04-17-fuel-core-consensus-f7826d1c1b`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `consensus-liveness`

## Code Shape Summary

- Vote tallying keyed the quorum map by a tuple of volatile epoch and block id, splitting one logical block into multiple groups.

## Search Motifs

- HashMap<(epoch, BlockId)> vote groups
- same block different epoch metadata
- group votes by block_id only
- max_epoch used only as tie breaker

## Typical Asymmetry

- The vulnerable shape appears when one path carries security context, freshness, resource accounting, or lifecycle state while an equivalent path silently omits it.
- Look for accepted variants, cached objects, async clones, or API resolvers that bypass the shared enforcement point.

## Patch Pattern

- Group reconciliation votes by BlockId only, preserve maximum epoch as metadata for tie-breaking, and add a regression test for the observed deadlock.

## False Match Warnings

- No issue if epoch is part of canonical block identity.
- No issue if mismatched epochs indicate genuinely different consensus objects that must not be grouped.
