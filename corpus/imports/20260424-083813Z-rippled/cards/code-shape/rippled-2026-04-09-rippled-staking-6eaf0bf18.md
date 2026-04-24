# Code-Shape Card

## Metadata

- ID: `rippled-2026-04-09-rippled-staking-6eaf0bf18`
- Bug family: `authz_and_role_gates`
- Bug class: `authorization-lifecycle-cleanup`

## Code Shape Summary

- The patch adds bidirectional owner-directory tracking for Delegate ledger entries. Creation now inserts the Delegate object into the authorized account's owner directory and stores the page in optional sfDestinationNode; deletion now removes the object from that authorized... Reusable shape: check for authorization was incomplete, late, or split across paths; the fix makes the gate explicit before the sensitive state change.

## Search Motifs

- Motif 1: authorization-check-path missing exact authorization check before privileged account action, delegated permission, or role-scoped state change
- Motif 2: security-sensitive path reaches privileged account action, delegated permission, or role-scoped state change before rejecting malformed, stale, or unauthorized input
- Motif 3: Maintain directory indexes for both accounts involved in a two-account ledger relationship, and persist the secondary directory page so deletion can remove the object from every directory where it was inserted.

## Typical Asymmetry

- Small externally controlled inputs or partially trusted protocol objects can cross into privileged account action, delegated permission, or role-scoped state change unless the authorization gate runs before the state-changing branch.

## Patch Pattern

- Maintain directory indexes for both accounts involved in a two-account ledger relationship, and persist the secondary directory page so deletion can remove the object from every directory where it was inserted.

## False Match Warnings

- No AccountDelete.cpp hunk is provided to show the exact cleanup path using the new index.
- No test hunk or output demonstrates an exploitable stale Delegate scenario.
