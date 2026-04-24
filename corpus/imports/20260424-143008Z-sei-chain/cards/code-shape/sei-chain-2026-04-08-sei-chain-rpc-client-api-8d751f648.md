# Code-Shape Card

## Metadata

- ID: `sei-chain-2026-04-08-sei-chain-rpc-client-api-8d751f648`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-protobuf-input-validation`

## Code Shape Summary

- The patch adds defensive protobuf conversion coverage and rejects an empty decoded TimeoutQC vote list at the protobuf-to-domain boundary before consensus objects are accepted.

## Search Motifs

- Motif 1: FromProto accepts empty TimeoutQC votes
- Motif 2: decode test expects no panic but no validation error
- Motif 3: proposal/domain object built before required field checks

## Typical Asymmetry

- The vulnerable shape separates a protocol decision from the later state-changing or resource-consuming sink, so one path observes or validates a value while another path commits effects using a broader, stale, defaulted, or unverified value.

## Patch Pattern

- Add decode-boundary validation for required fields and regression tests for malformed protobuf inputs.

## False Match Warnings

- The malformed object can only be constructed in tests and never from network/storage input.
- A later Verify call always rejects it before use.
