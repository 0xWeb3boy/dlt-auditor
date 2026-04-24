# Code-Shape Card

## Metadata

- ID: `sui-2022-07-29-sui-cryptography-24d683b660`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-malleability`

## Code Shape Summary

- The patch fixes secp256k1 recoverable signature malleability in `narwhal/crypto/src/secp256k1.rs`. The old verifier converted the recoverable signature to a standard ECDSA signature with `to_standard()` and verified that value against the public key.

## Search Motifs

- signature-canonicalization enforced after parsing but before cryptography state mutation
- cryptography handler accepts externally supplied protocol data
- alternate signed encodings accepted as equivalent
- missing epoch/domain/payload binding in verifier

## Typical Asymmetry

- The producer can vary signed bytes or context while the verifier accidentally treats distinct security domains as equivalent.

## Patch Pattern

- Verify recoverable signatures by recovering the public key from the exact recoverable signature and message, then comparing that recovered key to the expected public key. Do not reduce the signature to a standard ECDSA form when recovery metadata is part of the accepted signature representation.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
- The alternative encoding cannot be produced by an untrusted party or is normalized before verification.
