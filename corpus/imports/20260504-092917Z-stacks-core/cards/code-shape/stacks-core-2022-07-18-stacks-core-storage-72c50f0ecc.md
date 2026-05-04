# Code-Shape Card

## Metadata

- ID: `stacks-core-2022-07-18-stacks-core-storage-72c50f0ecc`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-domain-binding`

## Code Shape Summary

- The patch changes validator block proposal signing from a constant placeholder hash toward structured proposal-data signing that also takes a multiparty contract identifier, and it threads that contract through connection configuration into the RPC path. This is security-relevant cryptographic plumbing, but the provided evidence does not establish a concrete vulnerability, exploitability, or that pre-fix signatures were accepted in a dangerous context.

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
