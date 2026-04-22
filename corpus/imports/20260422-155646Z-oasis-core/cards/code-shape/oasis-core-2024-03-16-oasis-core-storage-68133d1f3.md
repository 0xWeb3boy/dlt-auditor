# Code-Shape Card

## Metadata

- ID: `oasis-core-2024-03-16-oasis-core-storage-68133d1f3`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `protocol-state-confusion`

## Code Shape Summary

- Short description of what the buggy code looked like: Inconsistent use of two related state coordinates ('round' versus 'handoff') across the CHURP subsystem. The evidence shows that some paths were bound to 'round' even though surrounding logic and comments indicate the operation is scoped to a handoff epoch.

## Search Motifs

- Motif 1: stale state reused across round, epoch, or restart boundaries
- Motif 2: update path bypasses the same validation as fresh admission
- Motif 3: lifecycle cleanup tied to the wrong transition marker

## Typical Asymmetry

- What was checked in one path but missing in another: The nominal path updated state correctly, but restart, timeout, overwrite, or lifecycle-transition paths left stale or mismatched state behind.

## Patch Pattern

- What the fix changed structurally: The patch updates both Go and Rust CHURP code so that requests are checked against the scheduled handoff epoch, persisted dealer material is loaded by handoff, and worker cleanup logic tracks handoff advancement instead of round advancement.

## False Match Warnings

- What looks similar but is often not a bug: Not a match if restart, timeout, overwrite, and update paths all clear or revalidate stale state before reuse.
