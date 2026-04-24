# Validation Card

## Metadata

- ID: `sei-chain-2024-03-19-sei-chain-transaction-processing-d63321d8e`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `weak-signature-message-binding`

## What Confirmed The Issue

- Evidence 1: AssociateTx preprocessing previously called getAddresses with common.Hash{} for signature recovery.
- Evidence 2: The patch hashes atx.CustomMessage and uses that hash for getAddresses.

## What Could Have Invalidated It

- Compensating control 1: A later authorization check binds the same signature to the intended message.
- Compensating control 2: The association operation is disabled or only accepts locally generated txs.

## Severity Guidance

- Expected impact band: protocol-state-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: A later authorization check binds the same signature to the intended message.
- Caution 2: The association operation is disabled or only accepts locally generated txs.
