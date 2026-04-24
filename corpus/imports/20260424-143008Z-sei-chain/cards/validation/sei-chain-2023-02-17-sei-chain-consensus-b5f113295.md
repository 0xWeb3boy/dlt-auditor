# Validation Card

## Metadata

- ID: `sei-chain-2023-02-17-sei-chain-consensus-b5f113295`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-determinism-hardening`

## What Confirmed The Issue

- Evidence 1: Direct map iteration over voteMap is replaced with sorted denom key traversal.
- Evidence 2: Direct map iteration over belowThresholdVoteMap is replaced with sorted denom key traversal before Tally calls.

## What Could Have Invalidated It

- Compensating control 1: The iteration only builds logs or metrics.
- Compensating control 2: The final state is order-independent by construction.

## Severity Guidance

- Expected impact band: protocol-state-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: The iteration only builds logs or metrics.
- Caution 2: The final state is order-independent by construction.
