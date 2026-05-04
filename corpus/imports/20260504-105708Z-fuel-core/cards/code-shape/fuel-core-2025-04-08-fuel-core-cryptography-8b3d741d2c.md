# Code-Shape Card

## Metadata

- ID: `fuel-core-2025-04-08-fuel-core-cryptography-8b3d741d2c`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-binding-hardening`

## Code Shape Summary

- A p2p delegation message carried a signed delegate key and a nonce as separate fields, leaving freshness metadata outside the signature boundary.

## Search Motifs

- Delegate { nonce, signed_key }
- nonce moved into sealed entity
- SignedByBlockProducerDelegation includes nonce
- delegate key replay hardening

## Typical Asymmetry

- The vulnerable shape appears when one path carries security context, freshness, resource accounting, or lifecycle state while an equivalent path silently omits it.
- Look for accepted variants, cached objects, async clones, or API resolvers that bypass the shared enforcement point.

## Patch Pattern

- Move nonce into the signed delegate-key entity and update producers, consumers, and tests to sign and verify the combined object.

## False Match Warnings

- No issue if the external nonce is independently MACed or checked against an authenticated transcript.
- No issue if nonce is informational and not used for replay protection.
