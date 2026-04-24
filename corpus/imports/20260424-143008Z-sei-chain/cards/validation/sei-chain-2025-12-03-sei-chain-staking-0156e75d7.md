# Validation Card

## Metadata

- ID: `sei-chain-2025-12-03-sei-chain-staking-0156e75d7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-determinism-hardening`

## What Confirmed The Issue

- Evidence 1: Commit states resultsHash/app hash is derived from marshalled transaction results and only deterministic fields should be included.
- Evidence 2: Commit states precompile error return data populated with stringified errors can bubble into the consensus-included ABCI data field.

## What Could Have Invalidated It

- Compensating control 1: The iteration only builds logs or metrics.
- Compensating control 2: The final state is order-independent by construction.

## Severity Guidance

- Expected impact band: protocol-state-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: The iteration only builds logs or metrics.
- Caution 2: The final state is order-independent by construction.
