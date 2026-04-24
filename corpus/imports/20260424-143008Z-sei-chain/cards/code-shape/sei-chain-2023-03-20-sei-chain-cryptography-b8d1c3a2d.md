# Code-Shape Card

## Metadata

- ID: `sei-chain-2023-03-20-sei-chain-cryptography-b8d1c3a2d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `merkle-proof-structural-validation`

## Code Shape Summary

- Security fix in the Tendermint Merkle proof path. The patch changes malformed proof reconstruction from ambiguous nil-root behavior into explicit errors, and updates verification/output callers to stop on those errors.

## Search Motifs

- Motif 1: proof reconstruction returns nil instead of error
- Motif 2: Verify ignores malformed proof shape
- Motif 3: empty tree root path accepts non-empty proof

## Typical Asymmetry

- The vulnerable shape separates a protocol decision from the later state-changing or resource-consuming sink, so one path observes or validates a value while another path commits effects using a broader, stale, defaulted, or unverified value.

## Patch Pattern

- Return explicit errors for invalid proof structure and require all verification/output callers to propagate them.

## False Match Warnings

- Callers already reject nil roots and malformed trees before verification.
- The proof is generated locally and never crosses a trust boundary.
