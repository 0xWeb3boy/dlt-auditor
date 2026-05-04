# Code-Shape Card

## Metadata

- ID: `stacks-core-2024-02-27-stacks-core-p2p-networking-a7e114be3c`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `inconsistent-signer-transaction-validation`

## Code Shape Summary

- The patch appears to centralize vote-transaction filtering in `NakamotoSigners` and apply that shared logic from signer and miner paths. This may be security relevant because it touches signer transaction validation, but the supplied evidence does not prove that invalid transactions could be executed, finalized, replayed, or used to cause a consensus failure before the patch. Structural cue: In `stacks-signer/src/signer.rs`, the patch removes `fn parse_vote_for_aggregate_public_key(`.

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
