# Code-Shape Card

## Metadata

- ID: `sei-chain-2026-02-09-sei-chain-transaction-processing-d9f1de1a4`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `app-hash-state-accounting-inconsistency`

## Code Shape Summary

- The evidence supports a likely security-relevant app-hash/state-accounting consistency fix in sei-chain's giga EVM execution path. The patch changes consensus-critical block-processing code to preserve `stateDB.Finalize()` surplus, pass that surplus into deferred EVM transaction info instead of hardcoding zero, and flush giga-store writes before later BankKeeper and EndBlock reads.

## Search Motifs

- Motif 1: stateDB.Finalize surplus ignored
- Motif 2: deferred tx info hardcodes zero surplus
- Motif 3: alternate store not flushed before BankKeeper reads

## Typical Asymmetry

- The vulnerable shape separates a protocol decision from the later state-changing or resource-consuming sink, so one path observes or validates a value while another path commits effects using a broader, stale, defaulted, or unverified value.

## Patch Pattern

- Preserve finalized deltas, pass them through deferred metadata, and flush alternate store layers before canonical state reads.

## False Match Warnings

- The alternate path is disabled in production.
- Downstream reads use the same cached store and cannot observe stale data.
