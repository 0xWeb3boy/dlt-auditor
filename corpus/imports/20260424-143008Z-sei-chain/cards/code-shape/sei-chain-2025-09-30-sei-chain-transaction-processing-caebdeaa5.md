# Code-Shape Card

## Metadata

- ID: `sei-chain-2025-09-30-sei-chain-transaction-processing-caebdeaa5`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-panic-hardening`

## Code Shape Summary

- The patch hardens sei-chain block proposal/finalization handling by recovering non-upgrade panics in ProcessBlock, checking ProcessBlock errors in optimistic proposal processing and FinalizeBlocker, and rejecting proposals when IsTxGasless reports a recovered panic.

## Search Motifs

- Motif 1: ProcessBlock return error ignored
- Motif 2: recover panic but caller still accepts proposal
- Motif 3: IsTxGasless panic converted to false instead of rejection

## Typical Asymmetry

- The vulnerable shape separates a protocol decision from the later state-changing or resource-consuming sink, so one path observes or validates a value while another path commits effects using a broader, stale, defaulted, or unverified value.

## Patch Pattern

- Recover non-upgrade panics, propagate errors explicitly, and reject proposals or finalization steps when processing fails.

## False Match Warnings

- Panics are impossible for attacker-controlled input or are recovered at a higher consensus boundary.
- The failed path is simulation-only and cannot affect proposal acceptance.
