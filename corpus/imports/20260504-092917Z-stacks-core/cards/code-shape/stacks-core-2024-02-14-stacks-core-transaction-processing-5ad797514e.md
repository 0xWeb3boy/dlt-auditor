# Code-Shape Card

## Metadata

- ID: `stacks-core-2024-02-14-stacks-core-transaction-processing-5ad797514e`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signer-message-validation`

## Code Shape Summary

- The patch changes Nakamoto miner/signer coordination logic in testnet/stacks-node/src/nakamoto_node/miner.rs. It builds a signer slot-to-address map, filters signer-submitted transactions by origin address, begins nonce-related chainstate handling, and changes rejection accounting to use signer weights while skipping already-seen signer IDs.

## Search Motifs

- Motif 1: signature verified without domain or chain context
- Motif 2: signer slot mapped to transaction origin only after acceptance
- Motif 3: block or vote accepted before reward-set membership is checked

## Typical Asymmetry

- The producer, peer, signer, or caller can choose fields that the consumer later treats as authoritative unless the missing property is checked at the boundary.

## Patch Pattern

- Derive the canonical signing context, reject malformed preimages, and verify signer identity before accepting or relaying the signed message.

## False Match Warnings

- A later consensus layer may repeat the full signature check.
- The code may only build test fixtures or diagnostics and never trust external messages.
