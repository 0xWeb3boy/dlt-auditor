# Code-Shape Card

## Metadata

- ID: `sei-chain-2024-03-19-sei-chain-transaction-processing-d63321d8e`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `weak-signature-message-binding`

## Code Shape Summary

- Likely security fix in the EVM account association path. The patch changes AssociateTx preprocessing from recovering addresses against common.Hash{} to recovering against Keccak256Hash([]byte(atx.CustomMessage)). It also adds CustomMessage to the AssociateTx model, protobuf serialization/deserialization, and tests.

## Search Motifs

- Motif 1: signature recovery uses constant placeholder hash
- Motif 2: transaction model lacks signed message field
- Motif 3: preprocess derives signer before binding message bytes

## Typical Asymmetry

- The vulnerable shape separates a protocol decision from the later state-changing or resource-consuming sink, so one path observes or validates a value while another path commits effects using a broader, stale, defaulted, or unverified value.

## Patch Pattern

- Serialize the intended message and use its domain-separated hash for signer recovery.

## False Match Warnings

- A later authorization check binds the same signature to the intended message.
- The association operation is disabled or only accepts locally generated txs.
