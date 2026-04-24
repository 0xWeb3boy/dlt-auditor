# Validation Card

## Metadata

- ID: `sei-chain-2023-03-20-sei-chain-cryptography-b8d1c3a2d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `merkle-proof-structural-validation`

## What Confirmed The Issue

- Evidence 1: Commit subject says: Patch forging empty merkle tree attack vector.
- Evidence 2: Merkle proof reconstruction now errors when total == 1 has non-empty inner hashes.

## What Could Have Invalidated It

- Compensating control 1: Callers already reject nil roots and malformed trees before verification.
- Compensating control 2: The proof is generated locally and never crosses a trust boundary.

## Severity Guidance

- Expected impact band: protocol-state-integrity
- Expected severity band: high_or_medium

## False-Positive Cautions

- Caution 1: Callers already reject nil roots and malformed trees before verification.
- Caution 2: The proof is generated locally and never crosses a trust boundary.
