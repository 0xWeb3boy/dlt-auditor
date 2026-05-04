# Validation Card

## Metadata

- ID: `zksync-era-2025-07-04-zksync-era-transaction-processing-ef0fdac4e`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-validation`

## What Confirmed The Issue

- Evidence 1: TEE proof submission now parses signatures with `PackedEthSignature::deserialize_packed` and rejects parse failures.
- Evidence 2: Signer recovery failure is mapped to an invalid-signature error instead of `unwrap()`, and the raw parser is restricted to tests.

## What Could Have Invalidated It

- Compensating control 1: The signature bytes are not caller-controlled or are already canonicalized before this path.
- Compensating control 2: A separate validation layer already rejects malformed signatures and catches recovery failures safely.

## Severity Guidance

- Expected impact band: proof-validation-hardening
- Expected severity band: medium

## False-Positive Cautions

- Caution 1: Do not claim forged proof acceptance without evidence that malformed signatures could pass signer authorization.
- Caution 2: Panic-risk reduction should be separated from proof-validity impact unless runtime availability effects are shown.
