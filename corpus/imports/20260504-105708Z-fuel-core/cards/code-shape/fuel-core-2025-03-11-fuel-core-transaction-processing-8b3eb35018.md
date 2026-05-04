# Code-Shape Card

## Metadata

- ID: `fuel-core-2025-03-11-fuel-core-transaction-processing-8b3eb35018`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `missing-signature-verification`

## Code Shape Summary

- The handler unpacked a sealed preconfirmation payload and applied embedded statuses directly, discarding or bypassing the signature-verification result.

## Search Motifs

- Sealed payload destructured before verification
- check_preconfirmation_signature added
- preconfirmation status update without signature check
- fake signature verifier regression

## Typical Asymmetry

- The vulnerable shape appears when one path carries security context, freshness, resource accounting, or lifecycle state while an equivalent path silently omits it.
- Look for accepted variants, cached objects, async clones, or API resolvers that bypass the shared enforcement point.

## Patch Pattern

- Verify the sealed preconfirmation signature before applying status updates and add tests for invalid-signature rejection.

## False Match Warnings

- No issue if the message source is authenticated by a stronger channel and payload signatures are redundant by design.
- No issue if statuses are never exposed or trusted by clients.
