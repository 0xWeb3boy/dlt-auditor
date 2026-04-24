# Validation Card

## Metadata

- ID: `sei-chain-2024-05-09-sei-chain-transaction-processing-b36bfe41b`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `replay-or-signature-validation`

## What Confirmed The Issue

- Evidence 1: Adds configured chain ID lookup via evmKeeper.ChainID(ctx) in EVMSigVerifyDecorator.AnteHandle.
- Evidence 2: Reads ethTx.ChainId() and validates it before later ante processing.

## What Could Have Invalidated It

- Compensating control 1: A later signer implementation rejects mismatched chain IDs before state changes.
- Compensating control 2: The path is simulation-only and cannot broadcast transactions.

## Severity Guidance

- Expected impact band: authorization-or-identity-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: A later signer implementation rejects mismatched chain IDs before state changes.
- Caution 2: The path is simulation-only and cannot broadcast transactions.
