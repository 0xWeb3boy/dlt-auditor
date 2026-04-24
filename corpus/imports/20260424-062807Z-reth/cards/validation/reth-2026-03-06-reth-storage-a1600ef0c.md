# Validation Card

## Metadata

- ID: `reth-2026-03-06-reth-storage-a1600ef0c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `proof-integrity`

## What Confirmed The Issue

- Commit message states the old behavior generated invalid proofs in release builds.
- The code change removes a special-case guard and always clears the final surviving hashed bit when masking leaves only one hashed child.

## What Could Have Invalidated It

- No evidence shows untrusted input or attacker-controlled reachability to this path
- No downstream verification or consensus failure is demonstrated in the patch itself

## Severity Guidance

- Expected impact band: state_or_proof_integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No evidence shows untrusted input or attacker-controlled reachability to this path
- No downstream verification or consensus failure is demonstrated in the patch itself
