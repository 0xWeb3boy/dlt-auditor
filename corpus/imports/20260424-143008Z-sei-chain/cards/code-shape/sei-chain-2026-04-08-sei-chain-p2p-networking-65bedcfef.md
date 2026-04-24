# Code-Shape Card

## Metadata

- ID: `sei-chain-2026-04-08-sei-chain-p2p-networking-65bedcfef`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `p2p-peer-abuse-accounting-hardening`

## Code Shape Summary

- The evidence supports a refactor and lifecycle correction for mempool CheckTx failure accounting: peer penalty state was moved from TxMempool into the mempool Reactor, and the commit message says failure-counter entries were previously never cleaned up.

## Search Motifs

- Motif 1: TxMempool owns SenderNodeID failure map
- Motif 2: peer disconnect does not clean failure counter
- Motif 3: reactor knows peer lifecycle but accounting happens elsewhere

## Typical Asymmetry

- The vulnerable shape separates a protocol decision from the later state-changing or resource-consuming sink, so one path observes or validates a value while another path commits effects using a broader, stale, defaulted, or unverified value.

## Patch Pattern

- Move failure accounting into the p2p reactor, filter counted error classes, and clean counters with peer lifecycle events.

## False Match Warnings

- Counters are purely diagnostic and never affect peer treatment.
- A separate peer manager expires all counters reliably.
