# Code-Shape Card

## Metadata

- ID: `sei-chain-2025-07-31-sei-chain-cryptography-1da04435c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion`

## Code Shape Summary

- The patch adds bounds checks for excessive PartSetHeader.Total values in Tendermint consensus proposal and peer-state handling, plus a defensive fallback in NewPartSetFromHeader. The supported security thesis is resource-exhaustion prevention from oversized consensus block-part counts. The evidence does not support cryptographic, replay, signature-bypass, or consensus-safety claims beyond resource-control risk.

## Search Motifs

- Motif 1: PartSetHeader.Total used before MaxBlockPartsCount check
- Motif 2: NewPartSetFromHeader called on remote header
- Motif 3: proposal receive path lacks part-count bound

## Typical Asymmetry

- The vulnerable shape separates a protocol decision from the later state-changing or resource-consuming sink, so one path observes or validates a value while another path commits effects using a broader, stale, defaulted, or unverified value.

## Patch Pattern

- Check externally supplied size fields at every entrypoint and add defensive lower-layer guards for missed callers.

## False Match Warnings

- The field is already bounded by decoding or network framing before allocation.
- The value is locally derived from a verified block.
