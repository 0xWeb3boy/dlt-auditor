# Validation Card

## Metadata

- ID: `go-ethereum-2025-04-08-go-ethereum-transaction-processing-2e739fce5`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `mempool-resource-exhaustion`

## What Confirmed The Issue

- Evidence 1: Commit body states the constraints mitigate an attack involving blob transaction spam, eviction of other transactions, and later cancellation by draining funds.
- Evidence 2: BlobPool adds checkDelegationLimit to allow at most one in-flight executable transaction for delegated or pending-delegation senders.

## What Could Have Invalidated It

- Compensating control 1: Classify as txpool resource-control hardening for EIP-7702/blobpool interactions.
- Compensating control 2: Do not claim a complete fix for all cross-subpool races.

## Severity Guidance

- Expected impact band: medium
- Expected severity band: low

## False-Positive Cautions

- Caution 1: Classify as txpool resource-control hardening for EIP-7702/blobpool interactions.
- Caution 2: Do not claim a complete fix for all cross-subpool races.
