# Code-Shape Card

## Metadata

- ID: `oasis-core-2024-10-03-oasis-core-cryptography-0d2f546b2`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `stale-session-state`

## Code Shape Summary

- Short description of what the buggy code looked like: The visible issue is stale or shared session/request state management in the concurrent enclave RPC path. The evidence supports that session state was not explicitly cleared when remote enclave identity policy changed, and that peer feedback previously went through shared queue-based bookkeeping instead of direct request-bound submission.

## Search Motifs

- Motif 1: stale state reused across round, epoch, or restart boundaries
- Motif 2: update path bypasses the same validation as fresh admission
- Motif 3: lifecycle cleanup tied to the wrong transition marker

## Typical Asymmetry

- What was checked in one path but missing in another: The nominal path updated state correctly, but restart, timeout, overwrite, or lifecycle-transition paths left stale or mismatched state behind.

## Patch Pattern

- What the fix changed structurally: The patch makes 'update_enclaves' drain sessions when the remote enclave identity set changes, switches peer-feedback submission to direct transport submission keyed by 'request_id', and tightens a responder-session creation invariant with an 'expect' after cleanup. The accompanying test was updated for concurrent feedback behavior without command-queue flushing.

## False Match Warnings

- What looks similar but is often not a bug: Not a match if restart, timeout, overwrite, and update paths all clear or revalidate stale state before reuse.
