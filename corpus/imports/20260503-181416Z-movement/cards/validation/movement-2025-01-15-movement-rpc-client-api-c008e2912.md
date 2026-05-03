# Validation Card

## Metadata

- ID: `movement-2025-01-15-movement-rpc-client-api-c008e2912`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `missing-signature-verification`

## What Confirmed The Issue

- Before the patch, stream_read_from_height converted each DaBlob directly into a pass-through RPC response.
- After the patch, it calls verifier.verify(da_blob, height.as_u64()).await before serialization.
- The constructed verifier is InKnownSignersVerifier in the shown path, matching the missing signer-set check.

## What Could Have Invalidated It

- The endpoint is explicitly documented and typed as raw unauthenticated data.
- The DA stream source guarantees known-signer verification before this function receives blobs.
- Clients never use the response for trust-sensitive state or decisions.

## Severity Guidance

- Expected impact band: integrity_high
- Expected severity band: high_or_medium
- Rationale: This is confirmed by Phase 4 and sits at a trust boundary where unverified external DA data was returned to clients; severity can be high when clients rely on the response for protocol state.

## False-Positive Cautions

- Do not flag if the upstream stream already enforces the same known-signer verifier and passes only verified types.
- Do not claim transaction signature bypass unless the returned blob is used as transaction authorization.
