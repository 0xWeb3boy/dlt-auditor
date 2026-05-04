# Code-Shape Card

## Metadata

- ID: `stacks-core-2024-02-23-stacks-core-cryptography-e24f223a98`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signer-vote-message-validation`

## Code Shape Summary

- The patch replaces an implicit signer vote encoding based on raw 32-byte hashes, 33-byte hash-plus-marker messages, and first-32-byte slicing with an explicit serialized `NakamotoBlockVote` containing `signer_signature_hash` and `rejected`. This is plausibly security-relevant because it touches signer vote validation and signature result handling, but the supplied evidence does not establish an exploitable vulnerability, consensus break, signature forgery, or threshold-signature bypass.

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
