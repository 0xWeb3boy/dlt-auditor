# Validation Card

## Metadata

- ID: `go-ethereum-2015-04-29-go-ethereum-storage-4e0796771`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `canonical-chain-reorg-invariant`

## What Confirmed The Issue

- Evidence 1: Patch is in core ChainManager InsertChain, the canonical block import and reorg path.
- Evidence 2: Old logic detected fork handling with block.Number() <= cblock.Number(), which could miss a higher-total-difficulty fork that was further ahead.

## What Could Have Invalidated It

- Compensating control 1: Classify as security-hardening rather than confirmed security-fix.
- Compensating control 2: Limit the claim to canonical chain/reorg invariant enforcement.

## Severity Guidance

- Expected impact band: high
- Expected severity band: medium

## False-Positive Cautions

- Caution 1: Classify as security-hardening rather than confirmed security-fix.
- Caution 2: Limit the claim to canonical chain/reorg invariant enforcement.
