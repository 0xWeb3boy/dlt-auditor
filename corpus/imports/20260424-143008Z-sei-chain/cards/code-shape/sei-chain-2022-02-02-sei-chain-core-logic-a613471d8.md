# Code-Shape Card

## Metadata

- ID: `sei-chain-2022-02-02-sei-chain-core-logic-a613471d8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-determinism`

## Code Shape Summary

- Likely security fix for consensus determinism in IBC transfer error acknowledgements. The patch changes the transfer receive failure path from committing `err.Error()` directly into an acknowledgement to using a transfer-specific acknowledgement helper, and adds documentation warning that acknowledgement error strings are written into state and can cause app hash divergence across mixed patch versions.

## Search Motifs

- Motif 1: err.Error() is written into acknowledgement data
- Motif 2: failure return bytes are included in app hash or results hash
- Motif 3: module-specific deterministic acknowledgement helper exists but is bypassed

## Typical Asymmetry

- The vulnerable shape separates a protocol decision from the later state-changing or resource-consuming sink, so one path observes or validates a value while another path commits effects using a broader, stale, defaulted, or unverified value.

## Patch Pattern

- Replace raw error serialization with stable module acknowledgement/result constructors.

## False Match Warnings

- The error text is never committed or included in consensus results.
- All possible error strings are protocol constants identical across versions.
