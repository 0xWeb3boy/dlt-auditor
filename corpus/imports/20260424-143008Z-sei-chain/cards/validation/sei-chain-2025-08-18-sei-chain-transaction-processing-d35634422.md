# Validation Card

## Metadata

- ID: `sei-chain-2025-08-18-sei-chain-transaction-processing-d35634422`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unsafe-legacy-transaction-acceptance`

## What Confirmed The Issue

- Evidence 1: Preprocess now rejects ethTx.Protected() == false unless isBlockTest is enabled.
- Evidence 2: The old normal path used ethtypes.FrontierSigner{}.Hash(ethTx) for unprotected legacy transactions and continued sender derivation.

## What Could Have Invalidated It

- Compensating control 1: The network intentionally supports unprotected legacy transactions and scopes them safely.
- Compensating control 2: A later ante stage rejects the transaction before execution.

## Severity Guidance

- Expected impact band: authorization-or-identity-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: The network intentionally supports unprotected legacy transactions and scopes them safely.
- Caution 2: A later ante stage rejects the transaction before execution.
