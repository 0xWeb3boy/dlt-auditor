# Code-Shape Card

## Metadata

- ID: `stacks-core-2024-06-06-stacks-core-storage-a7c5a1f061`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `missing-signature-verification`

## Code Shape Summary

- The patch is likely a security fix in the P2P Nakamoto block receipt and relay paths. The provided evidence shows that pushed-block validation previously could finish after sortition/PoX checks, while unsolicited block handling had an explicit signer-check unimplemented validation placeholder. The patch adds reward-cycle and reward-set lookup to these paths and extends the validation call site with the burnchain, sortdb, and chainstate context needed for that check.

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
