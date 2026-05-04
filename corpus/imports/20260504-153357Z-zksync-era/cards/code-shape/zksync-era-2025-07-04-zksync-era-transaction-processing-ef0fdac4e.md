# Code-Shape Card

## Metadata

- ID: `zksync-era-2025-07-04-zksync-era-transaction-processing-ef0fdac4e`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-validation`

## Code Shape Summary

- The patch changes TEE proof signature validation from raw `Signature::from_electrum` plus unchecked `recover(...).unwrap()` to `PackedEthSignature::deserialize_packed` plus checked signer recovery. This is security-relevant because it affects cryptographic validation on the TEE proof submission path, but the provided evidence does not prove proof forgery or show the full downstream signer authorization check.

## Search Motifs

- Motif 1: Request-controlled signature bytes parsed with a low-level helper that can return fallback signatures.
- Motif 2: Signer recovery uses `unwrap()` or equivalent unchecked failure handling.
- Motif 3: Patch switches to domain-specific packed signature deserialization and explicit invalid-signature errors.

## Typical Asymmetry

- Cryptographic proof boundaries require strict encoding and checked recovery; permissive helpers may be fine in tests but dangerous on external inputs.

## Patch Pattern

- Use the domain-specific signature type, reject malformed encodings during parsing, and map recovery failure to a validation error.

## False Match Warnings

- Internally generated signatures, test-only helpers, or outer layers that already canonicalize and handle recovery failures weaken the match.
