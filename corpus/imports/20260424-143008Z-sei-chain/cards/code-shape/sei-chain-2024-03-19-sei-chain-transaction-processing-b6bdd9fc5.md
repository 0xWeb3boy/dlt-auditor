# Code-Shape Card

## Metadata

- ID: `sei-chain-2024-03-19-sei-chain-transaction-processing-b6bdd9fc5`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-message-binding`

## Code Shape Summary

- The patch changes AssociateTx preprocessing from recovering addresses over common.Hash{} to recovering over Keccak256(CustomMessage). Supporting changes carry CustomMessage through AssociateTx construction and protobuf serialization, and tests now sign an Ethereum Signed Message-prefixed payload.

## Search Motifs

- Motif 1: ecrecover over common.Hash{} or zero hash
- Motif 2: signed custom message not serialized with tx
- Motif 3: association preprocessing ignores Ethereum signed message prefix

## Typical Asymmetry

- The vulnerable shape separates a protocol decision from the later state-changing or resource-consuming sink, so one path observes or validates a value while another path commits effects using a broader, stale, defaulted, or unverified value.

## Patch Pattern

- Carry signed message bytes through transaction encoding and recover over the hash/domain expected by the signing flow.

## False Match Warnings

- The signature is checked again over the correct message before association state changes.
- The path is migration/test-only and not reachable by submitted transactions.
