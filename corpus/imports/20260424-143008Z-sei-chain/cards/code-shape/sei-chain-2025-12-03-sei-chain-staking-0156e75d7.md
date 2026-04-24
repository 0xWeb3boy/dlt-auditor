# Code-Shape Card

## Metadata

- ID: `sei-chain-2025-12-03-sei-chain-staking-0156e75d7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-determinism-hardening`

## Code Shape Summary

- Likely security fix for consensus nondeterminism in EVM precompile error handling. The provided evidence shows failed precompile calls previously returned stringified error bytes and now return nil data while still reporting execution failure.

## Search Motifs

- Motif 1: range over map in BeginBlocker or EndBlocker
- Motif 2: store lookup performed inside iterator loop
- Motif 3: ballot or denom processing lacks sorted key traversal

## Typical Asymmetry

- The vulnerable shape separates a protocol decision from the later state-changing or resource-consuming sink, so one path observes or validates a value while another path commits effects using a broader, stale, defaulted, or unverified value.

## Patch Pattern

- Collect unordered keys or iterator values first, sort or stage them, then perform deterministic state work.

## False Match Warnings

- The iteration only builds logs or metrics.
- The final state is order-independent by construction.
