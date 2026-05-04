# Code-Shape Card

## Metadata

- ID: `fuel-core-2026-04-23-fuel-core-storage-bf285299c4`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `leader-lease-release-delay`

## Code Shape Summary

- An async adapter clone used for background publishing carried ownership-sensitive drop state, so worker lifetime confused logical ownership checks.

## Search Motifs

- Arc strong_count controls lease release
- task clone carries drop_release_guard
- Drop skips release when strong_count != 1
- publish task clone nulls guard

## Typical Asymmetry

- The vulnerable shape appears when one path carries security context, freshness, resource accounting, or lifecycle state while an equivalent path silently omits it.
- Look for accepted variants, cached objects, async clones, or API resolvers that bypass the shared enforcement point.

## Patch Pattern

- Make the release guard optional, strip it from task-spawned clones, and make Drop release only for logical adapter owners.

## False Match Warnings

- No issue if leases always expire quickly and failover ignores explicit release.
- No issue if worker clones cannot outlive the owning adapter.
