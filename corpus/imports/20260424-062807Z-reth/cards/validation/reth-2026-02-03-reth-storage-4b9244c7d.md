# Validation Card

## Metadata

- ID: `reth-2026-02-03-reth-storage-4b9244c7d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incomplete-trie-proof-generation`

## What Confirmed The Issue

- Storage proof dispatch now forces root-level evidence for all storage targets, including storage-only non-existence cases.
- Empty subtries now emit an explicit EmptyRoot node instead of returning an empty proof result.

## What Could Have Invalidated It

- No reproducer showing that pre-patch proofs were accepted incorrectly across a trust boundary
- No test or commit message tying the bug to an attack scenario, consensus issue, or verifier bypass

## Severity Guidance

- Expected impact band: state_or_proof_integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No reproducer showing that pre-patch proofs were accepted incorrectly across a trust boundary
- No test or commit message tying the bug to an attack scenario, consensus issue, or verifier bypass
