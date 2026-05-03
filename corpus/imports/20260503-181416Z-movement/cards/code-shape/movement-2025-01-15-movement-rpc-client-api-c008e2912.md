# Code-Shape Card

## Metadata

- ID: `movement-2025-01-15-movement-rpc-client-api-c008e2912`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `missing-signature-verification`

## Code Shape Summary

- A DA light-node pass-through read stream serialized each DA blob directly into an RPC response. The fix wires a VerifierOperations implementation into the light-node type and calls verifier.verify(blob, height) before serializing only the verified inner blob.

## Search Motifs

- stream_read_from_height maps external blob directly into RPC response
- verifier object exists but is absent from read path
- patch adds generic VerifierOperations to service type
- response serializes Verified<T>::into_inner instead of raw blob

## Typical Asymmetry

- The write/verification side had verifier concepts, but the read/response side emitted raw DA blobs as trusted output.

## Patch Pattern

- Thread a verifier dependency into the stream service, verify each blob at its DA height before response construction, and change response serialization to consume verified inner data only.

## False Match Warnings

- Do not flag if the upstream stream already enforces the same known-signer verifier and passes only verified types.
- Do not claim transaction signature bypass unless the returned blob is used as transaction authorization.
- A public mirror endpoint may intentionally return unverified raw data if it is clearly typed and documented as untrusted.
