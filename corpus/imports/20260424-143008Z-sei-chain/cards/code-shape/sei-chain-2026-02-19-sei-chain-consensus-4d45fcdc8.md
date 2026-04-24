# Code-Shape Card

## Metadata

- ID: `sei-chain-2026-02-19-sei-chain-consensus-4d45fcdc8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-consensus-state-validation`

## Code Shape Summary

- The patch fixes a security-relevant state-integrity issue in the Autobahn consensus data path. Before the fix, PushQC could use a stale or unneeded incoming QC's range and headers during later mutation and block matching even though QC verification was only performed when needQC was true. The fix ties QC insertion and update signaling to needQC, and matches blocks against stored verified QC headers.

## Search Motifs

- Motif 1: needQC controls verification but not insertion
- Motif 2: incoming QC range used after verification skipped
- Motif 3: block matched against unstored incoming header

## Typical Asymmetry

- The vulnerable shape separates a protocol decision from the later state-changing or resource-consuming sink, so one path observes or validates a value while another path commits effects using a broader, stale, defaulted, or unverified value.

## Patch Pattern

- Apply the same needed-and-verified predicate to verification, insertion, update signaling, and dependent block matching.

## False Match Warnings

- All incoming QCs are verified before this function regardless of needQC.
- Later state mutation reads only canonical stored QC data.
