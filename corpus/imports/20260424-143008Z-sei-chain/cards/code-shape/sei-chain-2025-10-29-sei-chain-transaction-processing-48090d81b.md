# Code-Shape Card

## Metadata

- ID: `sei-chain-2025-10-29-sei-chain-transaction-processing-48090d81b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `mempool-nonce-bookkeeping`

## Code Shape Summary

- This patch fixes stale EVM pending-nonce bookkeeping in the CheckTx/mempool admission path. Before the fix, a transaction nonce could be recorded in the pending-nonce tracker before the transaction was actually accepted into active or pending mempool, and some later rejection paths did not roll that nonce back. That stale nonce could make a higher-nonce transaction appear eligible for promotion and block inclusion.

## Search Motifs

- Motif 1: pending nonce insert before mempool AddTx success
- Motif 2: rollback only on some rejection paths
- Motif 3: higher nonce promoted because rejected lower nonce remains tracked

## Typical Asymmetry

- The vulnerable shape separates a protocol decision from the later state-changing or resource-consuming sink, so one path observes or validates a value while another path commits effects using a broader, stale, defaulted, or unverified value.

## Patch Pattern

- Move nonce side effects to final admission or make rollback cover every later failure path.

## False Match Warnings

- The nonce tracker is advisory only and never affects promotion or block selection.
- All post-insert rejection paths defer a guaranteed rollback.
