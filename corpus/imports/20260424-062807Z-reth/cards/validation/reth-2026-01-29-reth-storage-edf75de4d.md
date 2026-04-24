# Validation Card

## Metadata

- ID: `reth-2026-01-29-reth-storage-edf75de4d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `atomicity-violation`

## What Confirmed The Issue

- The code adds pre_validate_reveal_chain specifically to ensure all nodes needed for branch collapse are accessible before any mutation occurs.
- The old logic only checked the immediate blinded child; the new helper validates deeper reveal dependencies including extension grandchildren.

## What Could Have Invalidated It

- No proof that an external attacker can reliably trigger the blinded-node failure path
- No evidence of acceptance of invalid state, consensus split, replay issue, or cross-node security impact

## Severity Guidance

- Expected impact band: state_or_proof_integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No proof that an external attacker can reliably trigger the blinded-node failure path
- No evidence of acceptance of invalid state, consensus split, replay issue, or cross-node security impact
