# Code-Shape Card

## Metadata

- ID: `sei-chain-2026-02-12-sei-chain-rpc-client-api-f45028f01`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-state-mismatch`

## Code Shape Summary

- The patch is a Tendermint consensus liveness/state-alignment fix for a halt described as caused by reconstructing a block from a bad proposal. It adds a commit-certificate-aware proposal mismatch check, centralizes proposal block reconstruction around current round state, avoids reconstructing over an existing ProposalBlock, and makes commit handling wait for block parts matching the certified PartSetHeader.

## Search Motifs

- Motif 1: commit BlockID differs from ProposalBlock BlockID
- Motif 2: reconstruct block without checking PartSetHeader from commit
- Motif 3: proposal mismatch not rejected during commit step

## Typical Asymmetry

- The vulnerable shape separates a protocol decision from the later state-changing or resource-consuming sink, so one path observes or validates a value while another path commits effects using a broader, stale, defaulted, or unverified value.

## Patch Pattern

- Treat the commit certificate as authoritative, ignore conflicting proposals, and fetch/reconstruct only parts matching the certified header.

## False Match Warnings

- The consensus state machine already clears conflicting proposal data before commit.
- Block parts are cryptographically bound and cannot be mixed across headers.
