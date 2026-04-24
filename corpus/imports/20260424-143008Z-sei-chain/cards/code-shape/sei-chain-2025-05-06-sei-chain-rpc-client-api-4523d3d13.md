# Code-Shape Card

## Metadata

- ID: `sei-chain-2025-05-06-sei-chain-rpc-client-api-4523d3d13`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `check-then-set-race`

## Code Shape Summary

- The patch hardens oracle transaction spam prevention by replacing a split read-then-write counter check in the ante decorator with a keeper-level `CheckAndSetSpamPreventionCounter` method that locks per validator address, checks the current block height, and updates the counter while holding the lock.

## Search Motifs

- Motif 1: Get counter then Set counter in separate ante calls
- Motif 2: per-validator lock absent around check/update
- Motif 3: same block height compared before write

## Typical Asymmetry

- The vulnerable shape separates a protocol decision from the later state-changing or resource-consuming sink, so one path observes or validates a value while another path commits effects using a broader, stale, defaulted, or unverified value.

## Patch Pattern

- Combine check-and-set in a keeper method guarded by an actor-scoped lock.

## False Match Warnings

- Ante handling for the actor is strictly serialized by the mempool/executor.
- A database transaction enforces uniqueness for the counter key.
