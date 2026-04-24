# Code-Shape Card

## Metadata

- ID: `sei-chain-2026-04-10-sei-chain-core-logic-107c8e793`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `protocol-validation-hardening`

## Code Shape Summary

- The patch tightens p2p mux stream-kind validation: missing kind on new inbound stream creation is rejected, and explicit kind mismatch on an existing stream now returns an error.

## Search Motifs

- Motif 1: new inbound stream accepts missing kind
- Motif 2: existing stream does not compare kind
- Motif 3: accept limit keyed by stream kind can be bypassed or confused

## Typical Asymmetry

- The vulnerable shape separates a protocol decision from the later state-changing or resource-consuming sink, so one path observes or validates a value while another path commits effects using a broader, stale, defaulted, or unverified value.

## Patch Pattern

- Require explicit stream kind at creation and reject kind mismatches against stored stream state.

## False Match Warnings

- The transport authenticates and fixes stream kind before mux handling.
- Kind is informational and not used for limits or routing.
