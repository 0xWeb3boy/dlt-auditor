# Validation Card

## Metadata

- ID: `sei-chain-2024-03-19-sei-chain-transaction-processing-b6bdd9fc5`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-message-binding`

## What Confirmed The Issue

- Evidence 1: AssociateTx preprocessing previously recovered addresses using common.Hash{} as the signed message input.
- Evidence 2: The patch now hashes atx.CustomMessage and passes that hash into getAddresses for signature recovery.

## What Could Have Invalidated It

- Compensating control 1: The signature is checked again over the correct message before association state changes.
- Compensating control 2: The path is migration/test-only and not reachable by submitted transactions.

## Severity Guidance

- Expected impact band: authorization-or-identity-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: The signature is checked again over the correct message before association state changes.
- Caution 2: The path is migration/test-only and not reachable by submitted transactions.
