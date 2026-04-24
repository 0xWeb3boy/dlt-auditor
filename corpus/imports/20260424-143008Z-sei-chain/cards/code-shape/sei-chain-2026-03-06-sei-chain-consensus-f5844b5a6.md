# Code-Shape Card

## Metadata

- ID: `sei-chain-2026-03-06-sei-chain-consensus-f5844b5a6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-safety`

## Code Shape Summary

- Likely security fix in the Autobahn consensus timeout path. The production change in `State.voteTimeout` stops constructing TimeoutVotes solely from the current `i.PrepareQC`; when that value is absent, it inherits `i.TimeoutQC.LatestPrepareQC()`.

## Search Motifs

- Motif 1: TimeoutVote built only from current PrepareQC
- Motif 2: view-change clears lock while TimeoutQC still carries it
- Motif 3: LatestPrepareQC not inherited across consecutive timeouts

## Typical Asymmetry

- The vulnerable shape separates a protocol decision from the later state-changing or resource-consuming sink, so one path observes or validates a value while another path commits effects using a broader, stale, defaulted, or unverified value.

## Patch Pattern

- When current-view lock state is absent, inherit the lock from the justifying certificate before constructing timeout votes.

## False Match Warnings

- The protocol forbids entering the new view without separately restoring the lock.
- Proposal verification independently rejects conflicts without relying on TimeoutVote PrepareQC.
