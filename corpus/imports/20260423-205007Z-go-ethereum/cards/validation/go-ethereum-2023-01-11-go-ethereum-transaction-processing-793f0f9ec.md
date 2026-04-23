# Validation Card

## Metadata

- ID: `go-ethereum-2023-01-11-go-ethereum-transaction-processing-793f0f9ec`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-accounting-hardening`

## What Confirmed The Issue

- Evidence 1: Adds Shanghai-gated rejection of contract-creation initcode larger than params.MaxInitCodeSize.
- Evidence 2: Adds EIP-3860 per-word initcode gas charging to IntrinsicGas for contract creation.

## What Could Have Invalidated It

- Compensating control 1: Classify as protocol resource-accounting hardening, not a proven vulnerability fix.
- Compensating control 2: Do not claim a concrete liveness failure from the patch alone.

## Severity Guidance

- Expected impact band: low
- Expected severity band: low

## False-Positive Cautions

- Caution 1: Classify as protocol resource-accounting hardening, not a proven vulnerability fix.
- Caution 2: Do not claim a concrete liveness failure from the patch alone.
