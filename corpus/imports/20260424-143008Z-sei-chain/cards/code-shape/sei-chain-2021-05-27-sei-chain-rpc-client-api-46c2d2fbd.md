# Code-Shape Card

## Metadata

- ID: `sei-chain-2021-05-27-sei-chain-rpc-client-api-46c2d2fbd`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `ibc-client-recovery-hardening`

## Code Shape Summary

- The patch simplifies the IBC ClientUpdateProposal recovery path by removing the proposal-supplied InitialHeight flow, adding keeper-level checks that the substitute is active and ahead of the subject, and copying the substitute client's latest consensus state rather than iterating over a caller-influenced historical range.

## Search Motifs

- Motif 1: proposal supplies initial height for client recovery
- Motif 2: range copy loop tolerates missing consensus states
- Motif 3: substitute client latest state is not checked before copy

## Typical Asymmetry

- The vulnerable shape separates a protocol decision from the later state-changing or resource-consuming sink, so one path observes or validates a value while another path commits effects using a broader, stale, defaulted, or unverified value.

## Patch Pattern

- Remove caller-controlled range selection, enforce substitute-client suitability, and copy the canonical latest consensus state.

## False Match Warnings

- The proposal fields are already constrained by governance validation and cannot affect copied state.
- The copied state is independently verified against the substitute client before storage.
