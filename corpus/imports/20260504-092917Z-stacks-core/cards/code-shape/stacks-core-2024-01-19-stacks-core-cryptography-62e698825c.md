# Code-Shape Card

## Metadata

- ID: `stacks-core-2024-01-19-stacks-core-cryptography-62e698825c`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signer-request-validation-hardening`

## Code Shape Summary

- The patch appears to add signer-side validation and rejection reporting around block signing flow, but the provided evidence does not establish a concrete vulnerability or exploit path. The strongest grounded changes are that `SignatureShareRequest` handling now calls `validate_signature_share_request()` and drops invalid requests, and miner block proposals with invalid signature hashes now produce a `BlockRejection` with `RejectCode::InvalidSignatureHash`.

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
