# Validation Card

## Metadata

- ID: `reth-2026-04-21-reth-storage-d92ad5aa3`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-state-binding`

## What Confirmed The Issue

- Overlay resolution now requires an explicit anchor_hash and returns ProviderResult, removing the implicit no-anchor path.
- Revert logic switched from comparing block numbers to comparing db_tip_block.hash against self.anchor_hash.

## What Could Have Invalidated It

- No reproducer, advisory, or test demonstrates attacker-triggerable impact
- No patch evidence shows invalid block acceptance, consensus split, or proof forgery

## Severity Guidance

- Expected impact band: state_or_proof_integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No reproducer, advisory, or test demonstrates attacker-triggerable impact
- No patch evidence shows invalid block acceptance, consensus split, or proof forgery
