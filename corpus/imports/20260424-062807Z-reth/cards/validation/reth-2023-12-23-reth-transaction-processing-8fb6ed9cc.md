# Validation Card

## Metadata

- ID: `reth-2023-12-23-reth-transaction-processing-8fb6ed9cc`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incorrect-fork-gating`

## What Confirmed The Issue

- The changed code is in validate_transaction_regarding_header, a consensus validation function.
- The patch corrects the activation check for Transaction::Eip1559 from Hardfork::Berlin to Hardfork::London.

## What Could Have Invalidated It

- No proof that this function is the sole enforcement point for EIP-1559 enablement
- No evidence of an observed exploit, chain split, or invalid block acceptance

## Severity Guidance

- Expected impact band: protocol_integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No proof that this function is the sole enforcement point for EIP-1559 enablement
- No evidence of an observed exploit, chain split, or invalid block acceptance
