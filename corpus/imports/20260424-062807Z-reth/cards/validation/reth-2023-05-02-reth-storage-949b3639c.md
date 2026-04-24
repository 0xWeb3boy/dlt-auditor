# Validation Card

## Metadata

- ID: `reth-2023-05-02-reth-storage-949b3639c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `invalid-ancestor-handling`

## What Confirmed The Issue

- The old canonicalization-error branch is replaced with a dedicated on_failed_canonical_forkchoice_update handler in on_forkchoice_updated.
- The new handler docstring explicitly says it determines whether the forkchoice head is invalid and returns immediately in that case.

## What Could Have Invalidated It

- No proof that the pre-patch behavior let an attacker make the node accept an invalid block as canonical
- No evidence of a demonstrated consensus split, slashing event, fund impact, or remote exploit path

## Severity Guidance

- Expected impact band: consensus_or_protocol_integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No proof that the pre-patch behavior let an attacker make the node accept an invalid block as canonical
- No evidence of a demonstrated consensus split, slashing event, fund impact, or remote exploit path
