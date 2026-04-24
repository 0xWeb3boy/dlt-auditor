# Code-Shape Card

## Metadata

- ID: `sei-chain-2026-02-19-sei-chain-cryptography-1a3758d85`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-proposal-validation-hardening`

## Code Shape Summary

- The patch appears to harden consensus proposal validation. The directly shown code adds proposal-level lane-range validation and rejects `NewProposal` calls made with a key that is not the view leader. The commit summary additionally claims `FullProposal.

## Search Motifs

- Motif 1: NewProposal does not check key is view leader
- Motif 2: lane range not checked against committee
- Motif 3: FullProposal Verify omits actual proposer signature or LaneQC hash check

## Typical Asymmetry

- The vulnerable shape separates a protocol decision from the later state-changing or resource-consuming sink, so one path observes or validates a value while another path commits effects using a broader, stale, defaulted, or unverified value.

## Patch Pattern

- Move role, range, signature, and hash-link checks into explicit proposal construction and verification paths.

## False Match Warnings

- The constructor is private and all callers already validate these invariants.
- The verifier rejects the malformed proposal before consensus state mutation.
