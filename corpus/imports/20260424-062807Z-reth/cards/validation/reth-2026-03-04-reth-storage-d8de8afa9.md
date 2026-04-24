# Validation Card

## Metadata

- ID: `reth-2026-03-04-reth-storage-d8de8afa9`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion`

## What Confirmed The Issue

- The commit subject explicitly says the change is to "bound storage hashing stages memory."
- Both hashing stages replace a threshold check on to_block - from_block with a check on total_range, tightening the heuristic around total outstanding work.

## What Could Have Invalidated It

- No evidence shows that an external attacker or peer can directly force this condition in a default deployment
- No crash, OOM, advisory, test, or bug report is provided to prove a concrete denial-of-service vulnerability

## Severity Guidance

- Expected impact band: availability_or_resource_exhaustion
- Expected severity band: medium_or_low

## False-Positive Cautions

- No evidence shows that an external attacker or peer can directly force this condition in a default deployment
- No crash, OOM, advisory, test, or bug report is provided to prove a concrete denial-of-service vulnerability
