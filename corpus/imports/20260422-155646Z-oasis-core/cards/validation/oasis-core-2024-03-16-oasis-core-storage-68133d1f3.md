# Validation Card

## Metadata

- ID: `oasis-core-2024-03-16-oasis-core-storage-68133d1f3`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `protocol-state-confusion`

## What Confirmed The Issue

- Evidence 1: The patch updates both Go and Rust CHURP code so that requests are checked against the scheduled handoff epoch, persisted dealer material is loaded by handoff, and worker cleanup logic tracks handoff advancement instead of round advancement.
- Evidence 2: The source finding states the invariant explicitly: CHURP request validation, persisted handoff-specific dealer state, and submission scheduling should all use the same canonical handoff epoch identifier. The diff supports that consistency invariant, but does not by itself establish a concrete security failure from the prior 'round'-based behavior.

## What Could Have Invalidated It

- Compensating control 1: Not a match if restart, timeout, overwrite, and update paths all clear or revalidate stale state before reuse.
- Compensating control 2: Not a match if old and new state coordinates are guaranteed equivalent for every reachable transition.

## Severity Guidance

- Expected impact band: `integrity_or_policy_enforcement`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Not a match if restart, timeout, overwrite, and update paths all clear or revalidate stale state before reuse.
- Caution 2: Not a match if old and new state coordinates are guaranteed equivalent for every reachable transition.
