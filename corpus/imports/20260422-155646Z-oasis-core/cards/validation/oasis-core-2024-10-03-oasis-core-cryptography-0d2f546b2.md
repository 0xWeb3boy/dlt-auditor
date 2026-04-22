# Validation Card

## Metadata

- ID: `oasis-core-2024-10-03-oasis-core-cryptography-0d2f546b2`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `stale-session-state`

## What Confirmed The Issue

- Evidence 1: The patch makes 'update_enclaves' drain sessions when the remote enclave identity set changes, switches peer-feedback submission to direct transport submission keyed by 'request_id', and tightens a responder-session creation invariant with an 'expect' after cleanup. The accompanying test was updated for concurrent feedback behavior without command-queue flushing.
- Evidence 2: The source finding states the invariant explicitly: If the allowed remote enclave identity set changes, cached secure RPC sessions should not continue unchanged under the old policy. Request-scoped peer feedback should remain tied to the originating request even when multiple sessions are active.

## What Could Have Invalidated It

- Compensating control 1: Not a match if restart, timeout, overwrite, and update paths all clear or revalidate stale state before reuse.
- Compensating control 2: Not a match if old and new state coordinates are guaranteed equivalent for every reachable transition.

## Severity Guidance

- Expected impact band: `integrity_or_policy_enforcement`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Not a match if restart, timeout, overwrite, and update paths all clear or revalidate stale state before reuse.
- Caution 2: Not a match if old and new state coordinates are guaranteed equivalent for every reachable transition.
