# Code-Shape Card

## Metadata

- ID: `stacks-core-2023-11-14-stacks-core-storage-3ae5e37f0e`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `cryptographic-signature-type-hardening`

## Code Shape Summary

- The patch changes Nakamoto stacker signatures from a generic `MessageSignature` placeholder to `SchnorrSignature`, converts them to `WSTSSignature` in `accept_block`, and rejects blocks whose stacker signature cannot be converted. This is plausibly security relevant because it affects consensus block acceptance and cryptographic signature representation, but the provided evidence does not establish that the old code accepted invalid blocks, bypassed signature verification, or caused a consensus vulnerability.

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
