# Validation Card

## Metadata

- ID: `rippled-2026-04-09-rippled-staking-6eaf0bf18`
- Bug family: `authz_and_role_gates`
- Bug class: `authorization-lifecycle-cleanup`

## What Confirmed The Issue

- Evidence 1: Delegate creation now inserts the object into the authorized account's owner directory.
- Evidence 2: The new code comment explicitly ties the secondary index to finding and cleanup when the authorized account is deleted.

## What Could Have Invalidated It

- Compensating control 1: No AccountDelete.cpp hunk is provided to show the exact cleanup path using the new index.
- Compensating control 2: No test hunk or output demonstrates an exploitable stale Delegate scenario.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: stale-authorization-state, incomplete-account-cleanup
- Expected severity band: medium_or_high

## False-Positive Cautions

- Caution 1: No AccountDelete.cpp hunk is provided to show the exact cleanup path using the new index.
- Caution 2: No test hunk or output demonstrates an exploitable stale Delegate scenario.
