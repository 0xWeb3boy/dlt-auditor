# Code-Shape Card

## Metadata

- ID: `agave-2026-01-09-agave-consensus-8cebdeb9b0`
- Bug family: `authz_and_role_gates`
- Bug class: `improper-vote-authorization-filtering`

## Code Shape Summary

- A vote packet ingestion layer verifies that a vote account has stake but mutates latest-vote state without first matching the signer against the current epoch authorized-voter map.

## Search Motifs

- update_latest_vote before authorized voter check
- stake presence checked without epoch_authorized_voters lookup
- vote packet signer not compared to authorized voter
- insert batch with replenish accepts unauthorized vote

## Typical Asymmetry

- The vulnerable shape trusts an earlier, broader, or non-consuming check while a later security-sensitive sink assumes the data, identity, quota, or state was fully validated.
- The fixed shape moves the check to the boundary that owns the sink, consumes/accounting resources at admission, or carries authenticity/state metadata forward explicitly.

## Patch Pattern

- Filter votes at the vote-storage ingestion boundary by current epoch authorized-voter mapping before updating latest-vote state.

## False Match Warnings

- The same layer verifies authorized voter before any state mutation.
- The updated state is purely diagnostic and never feeds scheduling, replay, or consensus logic.
- A lower layer cryptographically rejects unauthorized votes before this function is reachable.
